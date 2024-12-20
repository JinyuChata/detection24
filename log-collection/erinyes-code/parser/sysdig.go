package parser

import (
	"erinyes/conf"
	"erinyes/helper"
	"erinyes/logs"
	"fmt"
	"regexp"
	"strings"
	"time"
)

const (
	NASTR     string = "<NA>"
	NILSTR    string = ""
	PROCESS   string = "Process"    // process -> process
	NETWORKV1 string = "Network_V1" // process -> socket
	NETWORKV2 string = "Network_V2" // socket -> process
	FILEV1    string = "File_V1"    // process -> file
	FILEV2    string = "File_V2"    // file -> process
)

// syscall
const (
	// process
	SYS_FORK   string = "fork"
	SYS_VFORK  string = "vfork"
	SYS_CLONE  string = "clone"
	SYS_EXECVE string = "execve"

	// network
	// server
	SYS_BIND    string = "bind"
	SYS_LISTEN  string = "listen"
	SYS_ACCEPT  string = "accept"
	SYS_ACCEPT4 string = "accept4"
	// client
	SYS_CONNECT string = "connect"
	// communication
	SYS_SENDTO   string = "sendto"
	SYS_RECVFROM string = "recvfrom"

	// file
	SYS_OPEN   string = "open"
	SYS_OPENAT string = "openat"
	SYS_READ   string = "read"
	SYS_READV  string = "readv"
	SYS_WRITE  string = "write"
	SYS_WRITEV string = "writev"
)

const UNKNOWN string = "unknown"

type SysdigLog struct {
	Time          int64
	Tid           string // thread id
	ProcessName   string
	Pid           string
	VPid          string // pid in container
	Dir           string // direction
	EventType     string // syscall
	Fd            string
	PPid          string
	Cmd           string
	Ret           string // syscall return
	ContainerID   string
	ContainerName string
	Info          []string // syscall parameters
	HostID        string
	HostName      string
}

func Convert2Timestamp(timeStr string) (int64, error) {
	layout := "2006-01-02 15:04:05.999999999"
	loc, err := time.LoadLocation("Asia/Shanghai")
	if err != nil {
		return 0, err
	}
	t, err := time.ParseInLocation(layout, timeStr, loc)
	if err != nil {
		return 0, err
	}
	return t.UnixNano() / int64(time.Microsecond), nil
}

func Convert2Datetime(timestamp int64) (string, error) {
	timestamp /= 1000
	timeObj := time.Unix(0, timestamp*int64(time.Millisecond))
	//timeObj := time.Unix(0, timestamp*int64(time.Microsecond))
	loc, err := time.LoadLocation("Asia/Shanghai")
	if err != nil {
		return "", err
	}
	timeInTargetZone := timeObj.In(loc)

	formattedTime := timeInTargetZone.Format("2006-01-02 15:04:05.999999999")
	return formattedTime, nil
}

func SplitSysdigLine(rawLine string) (error, *SysdigLog) {
	fields := strings.Split(rawLine, "#")
	fmt.Println(fields)
	if len(fields) < 14 {
		return fmt.Errorf("not enough fileds"), nil
	}
	timestamp, err := Convert2Timestamp(fields[0])
	if err != nil {
		logs.Logger.Errorf("Parse datetime to timestamp failed, datetime is %s", fields[0]+" "+fields[1])
		return err, nil
	}
	return nil, &SysdigLog{
		Time:          timestamp,
		ProcessName:   fields[1],
		Tid:           fields[2],
		Pid:           fields[3],
		VPid:          fields[4],
		Dir:           fields[5],
		EventType:     fields[6],
		Fd:            fields[7],
		PPid:          fields[8],
		Cmd:           fields[9],
		Ret:           fields[10],
		ContainerID:   fields[11],
		ContainerName: fields[12],
		Info:          fields[13:],
		HostID:        conf.MockHostID,
		HostName:      conf.MockHostName,
	}
}

func (s *SysdigLog) IsProcessCall() bool {
	if s.EventType == SYS_CLONE ||
		s.EventType == SYS_FORK ||
		s.EventType == SYS_VFORK ||
		s.EventType == SYS_EXECVE {
		return true
	}
	return false
}

func IsSocket(fd string) bool {
	socketRegex := regexp.MustCompile(`^\d+\.\d+\.\d+\.\d+:\d+->\d+\.\d+\.\d+\.\d+:\d+$`)
	return socketRegex.MatchString(fd)
}

func (s *SysdigLog) IsNetCall() bool {
	if s.EventType == SYS_BIND ||
		s.EventType == SYS_LISTEN ||
		s.EventType == SYS_ACCEPT ||
		s.EventType == SYS_ACCEPT4 ||
		s.EventType == SYS_CONNECT ||
		s.EventType == SYS_SENDTO ||
		s.EventType == SYS_RECVFROM {
		return true
	} else if s.EventType == SYS_READ && IsSocket(s.Fd) ||
		s.EventType == SYS_WRITE && IsSocket(s.Fd) {
		return true
	}
	return false
}

func (s *SysdigLog) IsFileCall() bool {
	if s.EventType == SYS_WRITE ||
		s.EventType == SYS_WRITEV ||
		s.EventType == SYS_READ ||
		s.EventType == SYS_READV ||
		s.EventType == SYS_OPEN ||
		s.EventType == SYS_OPENAT {
		return true
	}
	return false
}

func (s *SysdigLog) MustExtractFourTuple() (string, string, string, string) {
	re := regexp.MustCompile(`(\d+\.\d+\.\d+\.\d+):(\d+)->(\d+\.\d+\.\d+\.\d+):(\d+)`)
	matches := re.FindStringSubmatch(s.Fd)
	leftIP, leftPort, rightIP, rightPort := matches[1], matches[2], matches[3], matches[4]

	if leftPort == "53" {
		return rightIP, rightPort, leftIP, leftPort
	}
	if rightPort == "53" {
		return leftIP, leftPort, rightIP, rightPort
	}

	if _, ok := conf.Config.IPMap[leftIP]; ok {
		return leftIP, leftPort, rightIP, rightPort
	}
	if _, ok := conf.Config.IPMap[rightIP]; ok {
		return rightIP, rightPort, leftIP, leftPort
	}

	if (leftIP == "localhost" || leftIP == "127.0.0.1") && (rightIP == "localhost" || rightIP == "127.0.0.1") {
		return "localhost", leftPort, "localhost", rightPort
	}

	logs.Logger.Warn(s.Fd + " needs to be checked")
	return leftIP, leftPort, rightIP, rightPort
}

func (s *SysdigLog) ExtractPort() (string, bool) {
	portRegex := regexp.MustCompile(`:::(\d+)`)
	matches := portRegex.FindStringSubmatch(s.Fd)
	if len(matches) < 2 {
		return "", false
	}
	return matches[1], true
}

func (s *SysdigLog) FilteredFilePath() string {
	if strings.HasPrefix(s.Fd, "/home/app/node_modules") {
		return "/home/app/node_modules"
	}
	return s.Fd
}

func (s *SysdigLog) IsNodeTriggerStartLog() bool {
	if len(s.Info) < 4 { // e.g. res=77 data=flag_data is uuid
		return false
	}
	if s.ProcessName == "node" && s.EventType == SYS_WRITE && s.Info[1] == "data=flag_data" {
		return true
	}
	return false
}

func (s *SysdigLog) IsNodeTriggerEndLog() bool {
	if len(s.Info) < 4 { // e.g. res=77 data=end_flag_data is uuid
		return false
	}
	if s.ProcessName == "node" && s.EventType == SYS_WRITE && s.Info[1] == "data=end_flag_data" {
		return true
	}
	return false
}

func (s *SysdigLog) IsOfwatchdogTriggerStartLog() bool {
	if len(s.Info) < 4 { // e.g. res=62 data=start_ofwatchdog_flag_data is uuid
		return false
	}
	if s.ProcessName == "fwatchdog" && s.EventType == SYS_WRITE && s.Info[1] == "data=start_ofwatchdog_flag_data" {
		return true
	}
	return false
}

func (s *SysdigLog) IsOfwatchdogTriggerEndLog() bool {
	if len(s.Info) < 4 { // e.g. res=62 data=start_ofwatchdog_flag_data is uuid
		return false
	}
	if s.ProcessName == "fwatchdog" && s.EventType == SYS_WRITE && s.Info[1] == "data=end_ofwatchdog_flag_data" {
		return true
	}
	return false
}

func (s *SysdigLog) ConvertSysOpen() (error, string) {
	if s.EventType != SYS_OPEN && s.EventType != SYS_OPENAT {
		return fmt.Errorf("not open syscall"), ""
	}
	flag := strings.Join(s.Info, " ")
	re := regexp.MustCompile(`flags=\d+\(([^)]+)\)`)
	match := re.FindStringSubmatch(flag)
	if len(match) < 2 {
		return fmt.Errorf("can't parse flag mode: %s", flag), ""
	}
	params := strings.Split(match[1], "|")
	for i, param := range params {
		params[i] = strings.TrimSpace(param)
	}

	set := make(map[string]bool)
	var result []string
	for _, v := range params {
		set[v] = true
	}
	writeParams := []string{"O_WRONLY", "O_RDWR", "O_APPEND", "O_CREAT", "O_TRUNC"}
	for _, v := range writeParams {
		if set[v] {
			result = append(result, v)
		}
	}
	if len(result) > 0 { // write
		return nil, SYS_WRITE
	} else if set["O_RDONLY"] { // read
		return nil, SYS_READ
	}
	return fmt.Errorf("can't convert this open syscall"), ""
}

func (s *SysdigLog) GetLastRequestUUID() string {
	if s.ProcessName == "fwatchdog" {
		if value, exist := conf.OfwatchdogRequestUUIDMap[s.HostID+"#"+s.ContainerID]; exist {
			if len(value) == 0 {
				return UNKNOWN
			}
			return helper.JoinKeys(value, ",")
		}
		return UNKNOWN
	}
	if value, exist := conf.NodeLastRequestUUIDMap[s.HostID+"#"+s.ContainerID]; exist {
		if value == "" {
			return UNKNOWN
		}
		return value
	}
	return UNKNOWN
}
