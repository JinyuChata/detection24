// Another version of http_runner
package executor

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"os/signal"
	"strings"
	"syscall"
	"time"
)

// HTTPFunctionRunner creates and maintains one process responsible for handling all calls
type HTTPFunctionRunner struct {
	ExecTimeout    time.Duration // ExecTimeout the maximum duration or an upstream function call
	ReadTimeout    time.Duration // ReadTimeout for HTTP server
	WriteTimeout   time.Duration // WriteTimeout for HTTP Server
	Process        string        // Process to run as fprocess
	ProcessArgs    []string      // ProcessArgs to pass to command
	Command        *exec.Cmd
	StdinPipe      io.WriteCloser
	StdoutPipe     io.ReadCloser
	Client         *http.Client
	UpstreamURL    *url.URL
	BufferHTTPBody bool
}

// Start forks the process used for processing incoming requests
func (f *HTTPFunctionRunner) Start() error {
	//pdchange
	fmt.Printf("Running %s", f.Process)
	straceCmd := "strace"
	straceArgsStr := "-ttt -q -o request.alastor -e trace=execve,fork,clone,open,socket,bind,listen,accept4,connect,sendto,recvfrom,chmod,chown,access,unlink,unlinkat -ff"
	straceparts := strings.Split(straceArgsStr, " ")
	originalCmd := append([]string{f.Process}, f.ProcessArgs...)
	tracingCmd := append(straceparts, originalCmd...)
	cmd := exec.Command(straceCmd, tracingCmd[0:]...)
	//cmd := exec.Command(f.Process, f.ProcessArgs...)

	var stdinErr error
	var stdoutErr error

	f.Command = cmd
	f.StdinPipe, stdinErr = cmd.StdinPipe()
	if stdinErr != nil {
		return stdinErr
	}

	f.StdoutPipe, stdoutErr = cmd.StdoutPipe()
	if stdoutErr != nil {
		return stdoutErr
	}

	errPipe, _ := cmd.StderrPipe()

	// Logs lines from stderr and stdout to the stderr and stdout of this process
	bindLoggingPipe("stderr", errPipe, os.Stderr)
	bindLoggingPipe("stdout", f.StdoutPipe, os.Stdout)

	f.Client = makeProxyClient(f.ExecTimeout)

	go func() {
		sig := make(chan os.Signal, 1)
		signal.Notify(sig, syscall.SIGTERM)

		<-sig
		cmd.Process.Signal(syscall.SIGTERM)

	}()

	err := cmd.Start()
	go func() {
		err := cmd.Wait()
		if err != nil {
			log.Fatalf("Forked function has terminated: %s", err.Error())
		}
	}()

	return err
}

// Run a function with a long-running process with a HTTP protocol for communication
func (f *HTTPFunctionRunner) Run(req FunctionRequest, contentLength int64, r *http.Request, w http.ResponseWriter) error {
	/*The existence of reqscheduled file proves that at least one request was
	scheduled here*/
	_, e := os.Stat("reqscheduled")
	if e != nil {
		// Checking if the given file exists or not
		// Using IsNotExist() function
		if os.IsNotExist(e) {
			emptyfile, _ := os.Create("reqscheduled")
			emptyfile.Close()
		}
	}

	startedTime := time.Now()

	upstreamURL := f.UpstreamURL.String()

	if len(r.RequestURI) > 0 {
		upstreamURL += r.RequestURI
	}

	var body io.Reader
	if f.BufferHTTPBody {
		reqBody, _ := ioutil.ReadAll(r.Body)
		body = bytes.NewReader(reqBody)
	} else {
		body = r.Body
	}

	request, _ := http.NewRequest(r.Method, upstreamURL, body)
	for h := range r.Header {
		request.Header.Set(h, r.Header.Get(h))
	}
	log.Printf("Request ID: %s", r.Header.Get("x-call-id"))

	request.Host = r.Host
	copyHeaders(request.Header, &r.Header)

	var reqCtx context.Context
	var cancel context.CancelFunc

	if f.ExecTimeout.Nanoseconds() > 0 {
		reqCtx, cancel = context.WithTimeout(r.Context(), f.ExecTimeout)
	} else {
		//log.Printf("I am not setting timeout")
		reqCtx = r.Context()
		cancel = func() {

		}
	}

	defer cancel()

	res, err := f.Client.Do(request.WithContext(reqCtx))

	if err != nil {
		fmt.Printf("Upstream HTTP request error: %s\n", err.Error())

		// Error unrelated to context / deadline
		if reqCtx.Err() == nil {
			w.Header().Set("X-Duration-Seconds", fmt.Sprintf("%f", time.Since(startedTime).Seconds()))

			w.WriteHeader(http.StatusInternalServerError)

			return nil
		}

		select {
		case <-reqCtx.Done():
			{
				if reqCtx.Err() != nil {
					// Error due to timeout / deadline
					fmt.Printf("Upstream HTTP killed due to exec_timeout: %s\n", f.ExecTimeout)
					w.Header().Set("X-Duration-Seconds", fmt.Sprintf("%f", time.Since(startedTime).Seconds()))

					w.WriteHeader(http.StatusGatewayTimeout)
					return nil
				}

			}
		}

		w.Header().Set("X-Duration-Seconds", fmt.Sprintf("%f", time.Since(startedTime).Seconds()))
		w.WriteHeader(http.StatusInternalServerError)
		return err
	}

	copyHeaders(w.Header(), &res.Header)

	log.Printf("X-Duration-Seconds: %f", time.Since(startedTime).Seconds())
	w.Header().Set("X-Duration-Seconds", fmt.Sprintf("%f", time.Since(startedTime).Seconds()))

	w.WriteHeader(res.StatusCode)
	if res.Body != nil {
		defer res.Body.Close()

		bodyBytes, bodyErr := ioutil.ReadAll(res.Body)
		if bodyErr != nil {
			log.Println("read body err", bodyErr)
		}
		w.Write(bodyBytes)
	}

	//log.Printf("%s %s - %s - ContentLength: %d", r.Method, r.RequestURI, res.Status, res.ContentLength)

	//sendLogs() // this function is same in main.go and in here, this one sends
	//the logs for every request, while in main it just sends before container
	//is deleted
	return nil
}

func copyHeaders(destination http.Header, source *http.Header) {
	for k, v := range *source {
		vClone := make([]string, len(v))
		copy(vClone, v)
		(destination)[k] = vClone
	}
}

func makeProxyClient(dialTimeout time.Duration) *http.Client {
	//proxyUrl, _ := url.Parse("http://127.0.0.1:8082")
	proxyClient := http.Client{
		Transport: &http.Transport{
			Proxy: http.ProxyFromEnvironment, // http.ProxyURL(proxyUrl), : pdchange
			DialContext: (&net.Dialer{
				Timeout:   dialTimeout,
				KeepAlive: 10 * time.Second,
			}).DialContext,
			MaxIdleConns:          100,
			MaxIdleConnsPerHost:   100,
			DisableKeepAlives:     false,
			IdleConnTimeout:       500 * time.Millisecond,
			ExpectContinueTimeout: 1500 * time.Millisecond,
		},
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
	//log.Printf("%+v\n", *proxyClient.Transport.Proxy.URL)
	return &proxyClient
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
	log.Printf("Sending logs to http://172.22.224.34:44444/")
	podName, _ := ioutil.ReadFile("/etc/hostname")
	podstr := string(podName[:])
	podstr = strings.TrimSpace(podstr)
	tarFile := fmt.Sprintf("%s.tar", podstr)
	tarCmd := fmt.Sprintf("tar -czf %s request.alastor*", tarFile)
	//tarCmd := fmt.Sprintf("find . -iname 'request.alastor.*' -print0 | tar
	//-czf %s -T -", tarFile)
	sendlogCmd := fmt.Sprintf("curl -F 'file=@%s' http://172.22.224.34:44444/", tarFile)
	fullCmd := fmt.Sprintf("%s; %s;", tarCmd, sendlogCmd)
	log.Printf(fullCmd)
	cmd := exec.Command("/bin/sh", "-c", fullCmd)
	err := cmd.Run()

	if err != nil {
		log.Println(err.Error())
		return
	}
}
