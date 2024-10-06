package parser_local

import (
	"bufio"
	"encoding/json"
	"fmt"
)

// ReqHandlerMessage represents the parsed information from a log line
type ReqHandlerMessage struct {
	Pid            int    `json:"pid"`
	XCallId        string `json:"x-call-id"`
	XForwardedFor  string `json:"x-forwarded-for"`
	XForwardedHost string `json:"x-forwarded-host"`
	XStartTime     string `json:"x-start-time"`
}

// ReqHandlerParser is a parser for the ReqHandlerMessage
type ReqHandlerParser struct {
	allReqCallbackHook []func(message *ReqHandlerMessage)
}

// NewReqHandlerParser creates a new ReqHandlerParser instance
func NewReqHandlerParser() *ReqHandlerParser {
	return &ReqHandlerParser{
		allReqCallbackHook: make([]func(message *ReqHandlerMessage), 0, 20),
	}
}

// RegisterAllReqHook registers a callback for req
func (p *ReqHandlerParser) RegisterAllReqHook(callback func(*ReqHandlerMessage)) {
	p.allReqCallbackHook = append(p.allReqCallbackHook, callback)
}

// StartParse reads from the given reader and parses strace log lines
func (p *ReqHandlerParser) StartParse(reader *bufio.Reader) {
	p.parse(reader)
}

// parse reads lines from the reader and parses strace log lines
func (p *ReqHandlerParser) parse(reader *bufio.Reader) {
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			break
		}

		result := p.parseLine(line)
		if result != nil {
			for _, callback := range p.allReqCallbackHook {
				callback(result)
			}
		}
	}
}

// parseLine parses the raw log and returns the parsed ReqHandlerMessage
func (p *ReqHandlerParser) parseLine(rawLog string) *ReqHandlerMessage {
	var logEntry map[string]interface{}
	err := json.Unmarshal([]byte(rawLog), &logEntry)
	if err != nil {
		return nil
	}

	request, ok := logEntry["request"].(map[string]interface{})
	if !ok {
		fmt.Printf("missing 'request' field in log entry")
		return nil
	}

	parsedLog := &ReqHandlerMessage{
		XCallId:        getStringField(request, "x-call-id"),
		XForwardedFor:  getStringField(request, "x-forwarded-for"),
		XForwardedHost: getStringField(request, "x-forwarded-host"),
		XStartTime:     getStringField(request, "x-start-time"),
		Pid:            int(logEntry["pid"].(float64)),
	}

	return parsedLog
}

func getStringField(data map[string]interface{}, field string) string {
	if value, ok := data[field]; ok {
		if strValue, ok := value.(string); ok {
			return strValue
		}
	}
	return ""
}
