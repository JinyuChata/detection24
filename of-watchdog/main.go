package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"strings"
	"sync/atomic"
	"syscall"
	"time"

	limiter "github.com/openfaas/faas-middleware/concurrency-limiter"
	"github.com/openfaas/of-watchdog/config"
	"github.com/openfaas/of-watchdog/executor"
	"github.com/openfaas/of-watchdog/metrics"
)

var (
	acceptingConnections int32
	cmdMitm              *(exec.Cmd)
	logfile              *os.File
)

func main() {
	setLogOutput()
	defer logfile.Close()
	var runHealthcheck bool

	flag.BoolVar(&runHealthcheck,
		"run-healthcheck",
		false,
		"Check for the a lock-file, when using an exec healthcheck. Exit 0 for present, non-zero when not found.")

	flag.Parse()

	if runHealthcheck {
		if lockFilePresent() {
			os.Exit(0)
		}

		fmt.Fprintf(os.Stderr, "unable to find lock file.\n")
		os.Exit(1)
	}

	atomic.StoreInt32(&acceptingConnections, 0)

	watchdogConfig := config.New(os.Environ())

	if len(watchdogConfig.FunctionProcess) == 0 && watchdogConfig.OperationalMode != config.ModeStatic {
		fmt.Fprintf(os.Stderr, "Provide a \"function_process\" or \"fprocess\" environmental variable for your function.\n")
		os.Exit(1)
	}

	requestHandler := buildRequestHandler(watchdogConfig)

	fmt.Printf("OperationalMode: %s\n", config.WatchdogMode(watchdogConfig.OperationalMode))

	httpMetrics := metrics.NewHttp()
	http.HandleFunc("/", metrics.InstrumentHandler(requestHandler, httpMetrics))
	http.HandleFunc("/_/health", makeHealthHandler())

	metricsServer := metrics.MetricsServer{}
	metricsServer.Register(watchdogConfig.MetricsPort)

	cancel := make(chan bool)

	go metricsServer.Serve(cancel)

	shutdownTimeout := watchdogConfig.HTTPWriteTimeout
	s := &http.Server{
		Addr:           fmt.Sprintf(":%d", watchdogConfig.TCPPort),
		ReadTimeout:    watchdogConfig.HTTPReadTimeout,
		WriteTimeout:   watchdogConfig.HTTPWriteTimeout,
		MaxHeaderBytes: 1 << 20, // Max header of 1MB
	}

	fmt.Printf("Timeouts: read: %s, write: %s hard: %s.\n",
		watchdogConfig.HTTPReadTimeout,
		watchdogConfig.HTTPWriteTimeout,
		watchdogConfig.ExecTimeout)
	fmt.Printf("Listening on port: %d\n", watchdogConfig.TCPPort)

	// Start the mitmproxy
	startMitmproxy()

	listenUntilShutdown(shutdownTimeout, s, watchdogConfig.SuppressLock)
	sendLogs()
}

func markUnhealthy() error {
	atomic.StoreInt32(&acceptingConnections, 0)

	path := filepath.Join(os.TempDir(), ".lock")
	fmt.Printf("Removing lock-file : %s\n", path)
	removeErr := os.Remove(path)
	return removeErr
}

func listenUntilShutdown(shutdownTimeout time.Duration, s *http.Server, suppressLock bool) {

	idleConnsClosed := make(chan struct{})
	go func() {
		sig := make(chan os.Signal, 1)
		signal.Notify(sig, syscall.SIGTERM)

		<-sig

		fmt.Printf("SIGTERM received.. shutting down server in %s\n", shutdownTimeout.String())

		healthErr := markUnhealthy()

		if healthErr != nil {
			fmt.Printf("Unable to mark unhealthy during shutdown: %s\n", healthErr.Error())
		}

		<-time.Tick(shutdownTimeout)

		if err := s.Shutdown(context.Background()); err != nil {
			// Error from closing listeners, or context timeout:
			fmt.Printf("Error in Shutdown: %v", err)
		}

		fmt.Printf("No new connections allowed. Exiting in: %s\n", shutdownTimeout.String())

		<-time.Tick(shutdownTimeout)

		close(idleConnsClosed)
	}()

	// Run the HTTP server in a separate go-routine.
	go func() {
		if err := s.ListenAndServe(); err != http.ErrServerClosed {
			fmt.Printf("Error ListenAndServe: %v", err)
			close(idleConnsClosed)
		}
	}()

	if suppressLock == false {
		path, writeErr := createLockFile()

		if writeErr != nil {
			log.Panicf("Cannot write %s. To disable lock-file set env suppress_lock=true.\n Error: %s.\n", path, writeErr.Error())
		}
	} else {
		log.Println("Warning: \"suppress_lock\" is enabled. No automated health-checks will be in place for your function.")

		atomic.StoreInt32(&acceptingConnections, 1)
	}

	<-idleConnsClosed
}

func buildRequestHandler(watchdogConfig config.WatchdogConfig) http.Handler {
	var requestHandler http.HandlerFunc

	switch watchdogConfig.OperationalMode {
	case config.ModeStreaming:
		requestHandler = makeForkRequestHandler(watchdogConfig)
		break
	case config.ModeSerializing:
		requestHandler = makeSerializingForkRequestHandler(watchdogConfig)
		break
	case config.ModeAfterBurn:
		requestHandler = makeAfterBurnRequestHandler(watchdogConfig)
		break
	case config.ModeHTTP:
		requestHandler = makeHTTPRequestHandler(watchdogConfig)
		break
	case config.ModeStatic:
		requestHandler = makeStaticRequestHandler(watchdogConfig)
	default:
		log.Panicf("unknown watchdog mode: %d", watchdogConfig.OperationalMode)
		break
	}

	if watchdogConfig.MaxInflight > 0 {
		return limiter.NewConcurrencyLimiter(requestHandler, watchdogConfig.MaxInflight)
	}

	return requestHandler
}

// createLockFile returns a path to a lock file and/or an error
// if the file could not be created.
func createLockFile() (string, error) {
	path := filepath.Join(os.TempDir(), ".lock")
	fmt.Printf("Writing lock-file to: %s\n", path)

	mkdirErr := os.MkdirAll(os.TempDir(), os.ModePerm)
	if mkdirErr != nil {
		return path, mkdirErr
	}

	writeErr := ioutil.WriteFile(path, []byte{}, 0660)
	if writeErr != nil {
		return path, writeErr
	}

	atomic.StoreInt32(&acceptingConnections, 1)
	return path, nil
}

func makeAfterBurnRequestHandler(watchdogConfig config.WatchdogConfig) func(http.ResponseWriter, *http.Request) {
	fmt.Printf("Not supported\n")

	// commandName, arguments := watchdogConfig.Process()
	// functionInvoker := executor.AfterBurnFunctionRunner{
	// 	Process:     commandName,
	// 	ProcessArgs: arguments,
	// }

	// fmt.Printf("Forking %s %s\n", commandName, arguments)
	// functionInvoker.Start()

	// return func(w http.ResponseWriter, r *http.Request) {

	// 	req := executor.FunctionRequest{
	// 		Process:      commandName,
	// 		ProcessArgs:  arguments,
	// 		InputReader:  r.Body,
	// 		OutputWriter: w,
	// 	}

	// 	functionInvoker.Mutex.Lock()

	// 	err := functionInvoker.Run(req, r.ContentLength, r, w)

	// 	if err != nil {
	// 		w.WriteHeader(500)
	// 		w.Write([]byte(err.Error()))
	// 	}

	// 	functionInvoker.Mutex.Unlock()
	// }
	return nil
}

func makeSerializingForkRequestHandler(watchdogConfig config.WatchdogConfig) func(http.ResponseWriter, *http.Request) {
	functionInvoker := executor.SerializingForkFunctionRunner{
		ExecTimeout: watchdogConfig.ExecTimeout,
	}

	return func(w http.ResponseWriter, r *http.Request) {

		var environment []string

		if watchdogConfig.InjectCGIHeaders {
			environment = getEnvironment(r)
		}

		commandName, arguments := watchdogConfig.Process()
		req := executor.FunctionRequest{
			Process:       commandName,
			ProcessArgs:   arguments,
			InputReader:   r.Body,
			ContentLength: &r.ContentLength,
			OutputWriter:  w,
			Environment:   environment,
		}

		w.Header().Set("Content-Type", watchdogConfig.ContentType)
		err := functionInvoker.Run(req, w)
		if err != nil {
			log.Println(err)
		}
	}
}

func makeForkRequestHandler(watchdogConfig config.WatchdogConfig) func(http.ResponseWriter, *http.Request) {
	functionInvoker := executor.ForkFunctionRunner{
		ExecTimeout: watchdogConfig.ExecTimeout,
	}

	return func(w http.ResponseWriter, r *http.Request) {

		var environment []string

		if watchdogConfig.InjectCGIHeaders {
			environment = getEnvironment(r)
		}

		commandName, arguments := watchdogConfig.Process()
		req := executor.FunctionRequest{
			Process:      commandName,
			ProcessArgs:  arguments,
			InputReader:  r.Body,
			OutputWriter: w,
			Environment:  environment,
		}

		w.Header().Set("Content-Type", watchdogConfig.ContentType)
		err := functionInvoker.Run(req)
		if err != nil {
			log.Println(err.Error())

			// Probably cannot write to client if we already have written a header
			// w.WriteHeader(500)
			// w.Write([]byte(err.Error()))
		}
	}
}

func getEnvironment(r *http.Request) []string {
	var envs []string

	envs = os.Environ()
	for k, v := range r.Header {
		kv := fmt.Sprintf("Http_%s=%s", strings.Replace(k, "-", "_", -1), v[0])
		envs = append(envs, kv)
	}
	envs = append(envs, fmt.Sprintf("Http_Method=%s", r.Method))

	if len(r.URL.RawQuery) > 0 {
		envs = append(envs, fmt.Sprintf("Http_Query=%s", r.URL.RawQuery))
	}

	if len(r.URL.Path) > 0 {
		envs = append(envs, fmt.Sprintf("Http_Path=%s", r.URL.Path))
	}

	if len(r.TransferEncoding) > 0 {
		envs = append(envs, fmt.Sprintf("Http_Transfer_Encoding=%s", r.TransferEncoding[0]))
	}

	return envs
}

func makeHTTPRequestHandler(watchdogConfig config.WatchdogConfig) func(http.ResponseWriter, *http.Request) {
	commandName, arguments := watchdogConfig.Process()
	functionInvoker := executor.HTTPFunctionRunner{
		ExecTimeout:    watchdogConfig.ExecTimeout,
		Process:        commandName,
		ProcessArgs:    arguments,
		BufferHTTPBody: watchdogConfig.BufferHTTPBody,
	}

	if len(watchdogConfig.UpstreamURL) == 0 {
		log.Fatal(`For "mode=http" you must specify a valid URL for "http_upstream_url"`)
	}

	urlValue, upstreamURLErr := url.Parse(watchdogConfig.UpstreamURL)
	if upstreamURLErr != nil {
		log.Fatal(upstreamURLErr)
	}
	functionInvoker.UpstreamURL = urlValue

	fmt.Printf("Forking, with strace - %s %s\n", commandName, arguments)
	functionInvoker.Start()

	return func(w http.ResponseWriter, r *http.Request) {

		req := executor.FunctionRequest{
			Process:      commandName,
			ProcessArgs:  arguments,
			InputReader:  r.Body,
			OutputWriter: w,
		}

		if r.Body != nil {
			defer r.Body.Close()
		}

		err := functionInvoker.Run(req, r.ContentLength, r, w)

		if err != nil {
			w.WriteHeader(500)
			w.Write([]byte(err.Error()))
		}

	}
}

func makeStaticRequestHandler(watchdogConfig config.WatchdogConfig) http.HandlerFunc {
	if watchdogConfig.StaticPath == "" {
		log.Fatal(`For mode=static you must specify the "static_path" to serve`)
	}

	fmt.Printf("Serving files at %s", watchdogConfig.StaticPath)
	return http.FileServer(http.Dir(watchdogConfig.StaticPath)).ServeHTTP
}

func lockFilePresent() bool {
	path := filepath.Join(os.TempDir(), ".lock")

	if _, err := os.Stat(path); os.IsNotExist(err) {
		return false
	}
	return true
}

func makeHealthHandler() func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			if atomic.LoadInt32(&acceptingConnections) == 0 || lockFilePresent() == false {
				w.WriteHeader(http.StatusServiceUnavailable)
				return
			}

			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))

			break
		default:
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	}
}

func setLogOutput() {

	logfile, err := os.OpenFile("request.alastor.log", os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
	if err != nil {
		log.Fatal(err)
	}

	// BAD CODE: THE FOLLOWING CAUSED FILE TO CLOSE WHEN THIS FUNC RETURNS!
	// defer file.Close()

	log.SetOutput(logfile)
	log.Println("Logging to a file in Go!")
}

func sendLogs() {
	_, e := os.Stat("reqscheduled")
	if e != nil {
		// Checking if the given file exists or not
		// if no request came here no need to send logs
		if os.IsNotExist(e) {
			return
		}
	}
	fmt.Printf("Sending logs to http://172.22.224.34:44444/")
	podName, _ := ioutil.ReadFile("/etc/hostname")
	podstr := string(podName[:])
	podstr = strings.TrimSpace(podstr)
	tarFile := fmt.Sprintf("%s.tar", podstr)
	//tarCmd := fmt.Sprintf("find . -iname 'request.alastor.*' -print0 | tar
	//-cvf %s -T -", tarFile)
	tarCmd := fmt.Sprintf("tar -czf %s request.alastor*", tarFile)
	sendlogCmd := fmt.Sprintf("curl -F 'file=@%s' http://172.22.224.34:44444/", tarFile)
	fullCmd := fmt.Sprintf("%s; %s;", tarCmd, sendlogCmd)
	fmt.Printf(fullCmd)
	cmd := exec.Command("/bin/sh", "-c", fullCmd)
	err := cmd.Run()

	if err != nil {
		fmt.Println(err.Error())
		return
	}
}

func startMitmproxy() {
	log.Println("Starting mitmproxy now")
	//cmdArgs := []string{"--listen-port", "8082", "--listen-host", "127.0.0.1", "--showhost", "--set", "block_global=false", "--set", "confdir=/home/app/certs", "-w", "outfile"}

	cmdArgs := []string{"--listen-port", "8082", "--listen-host", "127.0.0.1", "--showhost", "--set", "block_global=false", "--set", "confdir=/home/app/certs", "-w", "outfile"}

	cmdMitm := exec.Command("mitmdump", cmdArgs...)
	stdout, _ := cmdMitm.StdoutPipe()

	f, _ := os.Create("nettaint.log")
	w := bufio.NewWriter(f)
	scanner := bufio.NewScanner(stdout)
	go func() {
		for scanner.Scan() {
			//fmt.Println(scanner.Text())
			fmt.Fprintln(w, scanner.Text())
			w.Flush()
		}
	}()

	if err := cmdMitm.Start(); err != nil {
		fmt.Printf("Failed to start cmd: %v\n", err)
		return
	}
}
