package parser_local

import (
	"bufio"
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// StraceMessage represents the parsed information from a strace log line
type StraceMessage struct {
	Timestamp  time.Time
	Pid        int
	SysType    string
	Args       []string
	Ret        int
	RetComment string
	Type       string
}

func (m StraceMessage) GetInet() (ip string, port int) {
	// 使用正则表达式提取端口号
	rePort := regexp.MustCompile(`htons\((\d+)\)`)
	reIpAddr := regexp.MustCompile(`inet_addr\("([\\.\d]+)"\)`)

	for _, arg := range m.Args {
		matches := rePort.FindStringSubmatch(arg)
		if len(matches) == 2 {
			port, _ = strconv.Atoi(matches[1])
			break
		}
	}

	for _, arg := range m.Args {
		matches := reIpAddr.FindStringSubmatch(arg)
		if len(matches) == 2 {
			ip = matches[1]
			break
		}
	}

	if ip == "" {
		ip = "0.0.0.0"
	}

	return
}

// StraceParser is responsible for parsing strace log lines
type StraceParser struct {
	allSyscallCallbackHook      []func(*StraceMessage)
	completeSyscallCallbackHook map[string][]func(*StraceMessage)
	rawSyscallCallbackHook      map[string][]func(*StraceMessage)
	reCompleteSyscall           *regexp.Regexp
	reUnfinishedSyscall         *regexp.Regexp
	reResumedSyscall            *regexp.Regexp
	pid                         int
	FdMapper                    map[int]map[int]string
}

// NewStraceParser creates a new instance of StraceParser
func NewStraceParser() *StraceParser {
	return &StraceParser{
		allSyscallCallbackHook:      make([]func(message *StraceMessage), 0, 20),
		completeSyscallCallbackHook: make(map[string][]func(*StraceMessage)),
		rawSyscallCallbackHook:      make(map[string][]func(*StraceMessage)),
		reCompleteSyscall:           regexp.MustCompile(`[\d\.]+ ([^(]+)\((.*)\)[ ]+=[ ]+([a-fx\d\-?]+)(.*)`),
		reUnfinishedSyscall:         regexp.MustCompile(`[\d\.]+ ([^(]+)\((.*) <unfinished \.\.\.>\s*`),
		reResumedSyscall:            regexp.MustCompile(`[\d\.]+ \<\.\.\. ([^ ]+) resumed\> (.*)\)[ ]+=[ ]+([a-fx\d\-?]+)(.*)`),
		pid:                         -1,
		FdMapper:                    map[int]map[int]string{},
	}
}

func (p *StraceParser) AddFdMap(pid int, fd int, name string) {
	if _, ok := p.FdMapper[pid]; !ok {
		p.FdMapper[pid] = make(map[int]string)
	}
	p.FdMapper[pid][fd] = name
}

func (p *StraceParser) SetPid(pid int) {
	p.pid = pid
}

// RegisterAllSyscallHook registers a callback for a all syscall
func (p *StraceParser) RegisterAllSyscallHook(callback func(*StraceMessage)) {
	p.allSyscallCallbackHook = append(p.allSyscallCallbackHook, callback)
}

// RegisterSyscallHook registers a callback for a specific syscall
func (p *StraceParser) RegisterSyscallHook(fullSyscallName string, callback func(*StraceMessage)) {
	p.completeSyscallCallbackHook[fullSyscallName] = append(p.completeSyscallCallbackHook[fullSyscallName], callback)
}

// RegisterRawSyscallHook registers a callback for a specific raw syscall
func (p *StraceParser) RegisterRawSyscallHook(fullSyscallName string, callback func(*StraceMessage)) {
	p.rawSyscallCallbackHook[fullSyscallName] = append(p.rawSyscallCallbackHook[fullSyscallName], callback)
}

// StartParse reads from the given reader and parses strace log lines
func (p *StraceParser) StartParse(reader *bufio.Reader) {
	p.parse(reader)
}

// parse reads lines from the reader and parses strace log lines
func (p *StraceParser) parse(reader *bufio.Reader) {
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			break
		}

		if strings.Contains(line, "restart_syscall") {
			continue
		}

		if strings.Contains(line, "+++ exited with") {
			continue
		}

		var unfinishedSyscall bool
		var reconstructSyscall bool
		var unfinishedSyscallStack map[string]string

		if strings.Contains(line, "<unfinished ...>") {
			unfinishedSyscall = true
			pid := strings.Fields(line)[0]
			unfinishedSyscallStack[pid] = line
		} else if strings.Contains(line, "resumed>") {
			pid := strings.Fields(line)[0]
			existLine, ok := unfinishedSyscallStack[pid]
			if ok {
				lineIndex := strings.Index(line, "resumed>") + len("resumed>")
				reconstructLine := strings.Replace(existLine, "<unfinished ...>", line[lineIndex:], 1)
				reconstructSyscall = true
				line = reconstructLine
			}
		}

		if unfinishedSyscall || reconstructSyscall {
			fmt.Printf("unfinished syscall: %v\n", unfinishedSyscall)
			fmt.Printf("reconstruct syscall: %v\n", reconstructSyscall)
		}

		result := p.parseLine(line)

		if result != nil {
			syscallName := result.SysType
			if callbacks, ok := p.rawSyscallCallbackHook[syscallName]; ok {
				for _, callback := range callbacks {
					callback(result)
				}
			}

			if callbacks, ok := p.completeSyscallCallbackHook[syscallName]; ok {
				for _, callback := range callbacks {
					callback(result)
				}
			}

			for _, callback := range p.allSyscallCallbackHook {
				callback(result)
			}
		}
	}
}

// parseLine parses a single strace log line and returns a StraceMessage
func (p *StraceParser) parseLine(line string) *StraceMessage {
	result := &StraceMessage{}

	ts, err := p.parseTimestamp(line)
	if err != nil {
		fmt.Printf("Parse timestamp with error %v", err)
		return nil
	}

	result.Timestamp = ts
	result.Pid = p.pid

	m := p.reUnfinishedSyscall.FindStringSubmatch(line)
	if m != nil {
		result.Type = "unfinished"
		result.SysType = m[1]
		result.Args = p.parseArgs(m[2])
		return result
	}

	m = p.reResumedSyscall.FindStringSubmatch(line)
	if m != nil {
		result.Type = "resumed"
		result.SysType = m[1]
		result.Args = p.parseArgs(m[2])
		result.Ret, _ = strconv.Atoi(m[3])
		result.RetComment = strings.TrimSpace(m[4])
		return result
	}

	m = p.reCompleteSyscall.FindStringSubmatch(line)
	if m != nil {
		result.Type = "completed"
		result.SysType = m[1]
		result.Args = p.parseArgs(m[2])
		result.Ret, _ = strconv.Atoi(m[3])
		result.RetComment = strings.TrimSpace(m[4])
		return result
	}

	return nil
}

// parseArgs parses the argument string and returns a list of arguments
func (p *StraceParser) parseArgs(argString string) []string {
	args := make([]string, 0)
	for _, arg := range strings.Split(argString, ", ") {
		args = append(args, strings.Trim(arg, " "))
	}
	return args
}

// parseTimestamp parses timestamp from raw timestr
func (p *StraceParser) parseTimestamp(rawStr string) (time.Time, error) {
	// 将字符串转换为浮点数
	timestampFloat, err := strconv.ParseFloat(strings.Split(rawStr, " ")[0], 64)
	if err != nil {
		return time.Time{}, err
	}

	// 将浮点数转换为Unix时间戳（秒）
	timestampInt := int64(timestampFloat)
	timestamp := time.Unix(timestampInt, 0)

	return timestamp, nil
}
