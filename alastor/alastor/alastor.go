package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"

	parser_local "github.com/JinyuChata/alastor/parser-local"
	"github.com/awalterschulze/gographviz"
)

type NodeType string

const gatewayIp = "NetPeer##10.1.80.247:8080"

const (
	Container = "Container"
	Process   = "Process"
	File      = "File"
	NetPeer   = "NetPeer"
	FD        = "Fd"
)

type AlastorParser struct {
	containerBase    string
	containerName    string
	straceParser     *parser_local.StraceParser
	reqHandlerParser *parser_local.ReqHandlerParser
}

func NewAlastorParser(containerBase string) *AlastorParser {
	return &AlastorParser{
		containerBase:    containerBase,
		containerName:    containerBase[strings.LastIndex(containerBase, "/")+1:],
		straceParser:     parser_local.NewStraceParser(),
		reqHandlerParser: parser_local.NewReqHandlerParser(),
	}
}

func (p *AlastorParser) listFiles(dirPath, pattern string) ([]string, error) {
	var matchingFiles []string

	re, err := regexp.Compile(pattern)
	if err != nil {
		return nil, err
	}

	err = filepath.Walk(dirPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			fileName := filepath.Base(path)
			if re.MatchString(fileName) {
				matchingFiles = append(matchingFiles, path)
			}
		}

		return nil
	})

	return matchingFiles, err
}

func (p *AlastorParser) parseStrace() {
	// prepare
	pattern := `^request\.alastor\.\d+$`
	files, err := p.listFiles(p.containerBase, pattern)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	for _, file := range files {
		f, err := os.Open(file)
		if err != nil {
			fmt.Println("Error opening file:", err)
			return
		}
		pidStr := file[strings.LastIndex(file, ".")+1:]
		pid, err := strconv.Atoi(pidStr)
		if err != nil {
			fmt.Println("Error pid:", err)
			return
		}
		reader := bufio.NewReader(f)
		p.straceParser.SetPid(pid)
		p.straceParser.StartParse(reader)
		f.Close()
	}
}

func (p *AlastorParser) parseReq() {
	// prepare
	file := path.Join(p.containerBase, "request.alastor.log")
	f, err := os.Open(file)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	reader := bufio.NewReader(f)
	p.reqHandlerParser.StartParse(reader)
	f.Close()
}

func (p *AlastorParser) displayNameProcess(pid int) string {
	return p.addQuotation(Process + "##" + strconv.Itoa(pid))
}

func (p *AlastorParser) displayNameContainer(containerName string) string {
	return p.addQuotation(Container + "##" + containerName)
}

func (p *AlastorParser) displayNameFile(fileName string) string {
	return p.addQuotation(File + "##" + fileName)
}

func (p *AlastorParser) displayNetPeer(ip string, port int) string {
	inet := fmt.Sprintf("%v:%v", ip, port)
	return p.addQuotation(NetPeer + "##" + inet)
}

func (p *AlastorParser) displayFd(fd string) string {
	return p.addQuotation(FD + "##" + fd)
}

func (p *AlastorParser) getShape(nodeType NodeType) string {
	if nodeType == Container {
		return "box"
	} else if nodeType == Process {
		return "box"
	} else if nodeType == FD {
		return "box"
	} else if nodeType == File {
		return "ellipse"
	} else if nodeType == NetPeer {
		return "diamond"
	} else {
		return "ellipse"
	}
}

func (p *AlastorParser) addQuotation(str string) string {
	return fmt.Sprintf("%q", str)
}

func (p *AlastorParser) BuildLocalGraph(dotPath string) {
	graphAst, _ := gographviz.Parse([]byte(`digraph G{}`))
	graph := gographviz.NewGraph()
	err := gographviz.Analyse(graphAst, graph)
	if err != nil {
		fmt.Println("Error init graph")
		return
	}

	// add container node
	nodeContainer := p.displayNameContainer(p.containerName)
	graph.AddNode("G", nodeContainer,
		map[string]string{"shape": p.addQuotation(p.getShape(Container))})

	// parse r.log
	// reqId: pid map
	reqPidMap := make(map[string]int)

	// register request handler
	p.reqHandlerParser.RegisterAllReqHook(func(msg *parser_local.ReqHandlerMessage) {
		nodeProcess := p.displayNameProcess(msg.Pid)
		reqPidMap[msg.XCallId] = msg.Pid
		graph.AddNode("G", nodeProcess,
			map[string]string{"shape": p.addQuotation(p.getShape(Process))})
		graph.AddEdge(nodeContainer, nodeProcess, true, map[string]string{
			//"label":      p.addQuotation(msg.XCallId),
			"label": fmt.Sprintf("\"%s\"", msg.XStartTime),
		})
	})
	p.parseReq()

	// parse strace
	procSyscalls := []string{"execve", "fork", "clone"}
	for _, procSyscall := range procSyscalls {
		p.straceParser.RegisterSyscallHook(procSyscall, func(msg *parser_local.StraceMessage) {
			childPid := msg.Ret
			if childPid > 0 {
				// child process generated
				//fmt.Printf("Process %v -> %v\n", msg.Pid, childPid)
				nodeParentProcess := p.displayNameProcess(msg.Pid)
				graph.AddNode("G", nodeParentProcess,
					map[string]string{"shape": p.addQuotation(p.getShape(Process))})
				nodeChildProcess := p.displayNameProcess(childPid)
				graph.AddNode("G", nodeChildProcess,
					map[string]string{"shape": p.addQuotation(p.getShape(Process))})
				graph.AddEdge(nodeParentProcess, nodeChildProcess, true, map[string]string{
					"label": fmt.Sprintf("\"%v\"", msg.Timestamp.UnixNano()),
				})
			}
		})
	}

	rwSyscalls := []string{"read", "write"}
	for _, rwSyscall := range rwSyscalls {
		p.straceParser.RegisterSyscallHook(rwSyscall, func(msg *parser_local.StraceMessage) {
			nodeProcess := p.displayNameProcess(msg.Pid)
			fd := msg.Args[0]
			fdNum, err := strconv.Atoi(fd)
			if err != nil {
				fmt.Errorf("%v invalid fd\n", fd)
			}
			fileName := fd
			if m, ok := p.straceParser.FdMapper[msg.Pid]; ok {
				if nme, okk := m[fdNum]; okk {
					fileName = nme
				}
			}
			if fileName == "1" {
				fileName = p.displayNameFile("STDOUT")
			} else if fileName == "0" {
				fileName = p.displayNameFile("STDIN")
			} else if fileName == "2" {
				fileName = p.displayNameFile("STDERR")
			} else if !strings.Contains(fileName, "#") {
				fileName = p.displayFd(fileName)
			}
			graph.AddNode("G", nodeProcess,
				map[string]string{"shape": p.addQuotation(p.getShape(Process))})
			graph.AddNode("G", fileName,
				map[string]string{"shape": p.addQuotation(p.getShape(FD))})
			if rwSyscall == "read" {
				graph.AddEdge(fileName, nodeProcess, true, map[string]string{
					"label": fmt.Sprintf("read:\"%v\"", msg.Timestamp.UnixNano()),
				})
			} else { // write
				graph.AddEdge(nodeProcess, fileName, true, map[string]string{
					"label": fmt.Sprintf("write:\"%v\"", msg.Timestamp.UnixNano()),
				})
			}
		})
	}

	netSyscalls := []string{"bind", "listen", "connect", "accept", "sendto", "recvfrom", "accept4"}
	for _, netSyscall := range netSyscalls {
		p.straceParser.RegisterSyscallHook(netSyscall, func(msg *parser_local.StraceMessage) {
			ip, port := msg.GetInet()
			nodeProcess := p.displayNameProcess(msg.Pid)

			if msg.SysType == "accept4" || msg.SysType == "listen" {
				port = 3000
			}
			graph.AddNode("G", nodeProcess,
				map[string]string{"shape": p.addQuotation(p.getShape(Process))})
			nodeInet := p.displayNetPeer(ip, port)
			graph.AddNode("G", nodeInet,
				map[string]string{"shape": p.addQuotation(p.getShape(NetPeer))})
			if msg.SysType == "accept4" {
				gIp := p.addQuotation(gatewayIp)
				graph.AddNode("G", gIp,
					map[string]string{"shape": p.addQuotation(p.getShape(NetPeer))})
				graph.AddEdge(nodeInet, gIp, true, map[string]string{
					"label": fmt.Sprintf("\"%v\"", msg.Timestamp.UnixNano()),
				})
				graph.AddEdge(gIp, nodeInet, true, map[string]string{
					"label": fmt.Sprintf("\"%v\"", msg.Timestamp.UnixNano()),
				})
			} else if msg.SysType == "recvfrom" || msg.SysType == "listen" {
				graph.AddEdge(nodeInet, nodeProcess, true, map[string]string{
					"label": fmt.Sprintf("\"%v\"", msg.Timestamp.UnixNano()),
				})
			} else {
				graph.AddEdge(nodeProcess, nodeInet, true, map[string]string{
					"label": fmt.Sprintf("\"%v\"", msg.Timestamp.UnixNano()),
				})
			}

			// add fd map
			if msg.SysType == "connect" {
				nodeInet := p.displayNetPeer(ip, port)
				fdNum, err := strconv.Atoi(msg.Args[0])
				if err != nil {
					fmt.Errorf("fdNum err \n")
				}
				p.straceParser.AddFdMap(msg.Pid, fdNum, nodeInet)
			} else if msg.SysType == "accept4" {
				gIp := p.addQuotation(gatewayIp)
				fdNum := msg.Ret
				if fdNum >= 0 {
					p.straceParser.AddFdMap(msg.Pid, fdNum, gIp)
				}
			}
		})
	}

	writeParams := []string{"O_WRONLY", "O_RDWR", "O_APPEND", "O_CREAT", "O_TRUNC"}
	p.straceParser.RegisterSyscallHook("open", func(msg *parser_local.StraceMessage) {
		filename := msg.Args[0]
		filename = strings.Trim(filename, "\"")

		if msg.Ret != -1 {
			p.straceParser.AddFdMap(msg.Pid, msg.Ret, p.displayNameFile(msg.Args[0]))
		}

		// CHECKME: skip node_modules ?
		if strings.Contains(filename, "node_modules") {
			return
		}

		nodeProcess := p.displayNameProcess(msg.Pid)
		graph.AddNode("G", nodeProcess,
			map[string]string{"shape": p.addQuotation(p.getShape(Process))})
		nodeFile := p.displayNameFile(filename)
		graph.AddNode("G", nodeFile,
			map[string]string{"shape": p.addQuotation(p.getShape(File))})

		openMod := msg.Args[1]
		isWrite := false
		for _, writeParam := range writeParams {
			if strings.Contains(openMod, writeParam) {
				isWrite = true
				break
			}
		}

		//fmt.Println(isWrite, openMod, filename)
		if isWrite {
			graph.AddEdge(nodeProcess, nodeFile, true, map[string]string{
				"label": fmt.Sprintf("\"%v\"", msg.Timestamp.UnixNano()),
			})
		} else if strings.Contains(openMod, "O_RDONLY") {
			graph.AddEdge(nodeFile, nodeProcess, true, map[string]string{
				"label": fmt.Sprintf("\"%v\"", msg.Timestamp.UnixNano()),
			})
		}
	})

	p.parseStrace()
	// output dot
	fo, err := os.OpenFile(dotPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, os.ModePerm)
	if err != nil {
		log.Fatal(err)
	}
	defer fo.Close()

	fo.WriteString(graph.String())

}

func main() {
	// logBase := "static/log"
	// dotBase := "static/dot"
	if len(os.Args) < 3 {
		fmt.Println("Usage: programName <logBase> <dotBase>")
		os.Exit(1)
	}

	logBase := os.Args[1]
	dotBase := os.Args[2]

	containerBaseList := make([]string, 0)
	entries, err := filepath.Glob(filepath.Join(logBase, "*-alastor-*"))
	if err != nil {
		fmt.Println(err)
	}

	for _, entry := range entries {
		containerBaseList = append(containerBaseList, entry)
	}

	// strace
	for _, containerBase := range containerBaseList {
		parser := NewAlastorParser(containerBase)
		parser.BuildLocalGraph(path.Join(dotBase, parser.containerName+".dot"))
	}

	//parser.straceParser.RegisterAllSyscallHook(func(msg *parser_local.StraceMessage) {
	//	fmt.Printf("Strace: %#v \n", msg)
	//})
	//parser.parseStrace(containerBase)
}
