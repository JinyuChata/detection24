package parser

import (
	"encoding/json"
	"erinyes/logs"
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type NetJson struct {
	IPSrc      string `json:"ip_src"`
	PortSrc    int    `json:"port_src"`
	IPDst      string `json:"ip_dst"`
	PortDst    int    `json:"port_dst"`
	SeqNum     int64  `json:"sequence_num"`
	AckNum     int64  `json:"acknowledge_num"`
	PayLoadLen int    `json:"payload_len"`
	PayLoad    string `json:"payload"`
	TimeStamp  string `json:"time_stamp"`
}

type NetLog struct {
	IPSrc      string
	PortSrc    string
	IPDst      string
	PortDst    string
	SeqNum     int64
	AckNum     int64
	PayLoadLen int
	Method     string
	Time       int64
	UUID       string
}

func SplitNetLine(rawLine string) (error, *NetLog) {
	var netJson NetJson
	err := json.Unmarshal([]byte(rawLine), &netJson)
	if err != nil {
		logs.Logger.WithError(err).Errorf("parse JSON failed")
		return err, nil
	}
	method := "UNKNOWN"
	index := strings.Index(netJson.PayLoad, " ")
	if index != -1 {
		firstStr := netJson.PayLoad[:index]
		if strings.HasPrefix(firstStr, "HTTP") { // response
			method = "RESPONSE"
		} else if firstStr == "GET" {
			method = "GET"
		} else if firstStr == "POST" {
			method = "POST"
		} else if firstStr == "DELETE" {
			method = "DELETE"
		} else if firstStr == "PUT" {
			method = "PUT"
		}
	}

	var uuid string
	uuidRegex := regexp.MustCompile(`uuid: ([a-zA-Z0-9]+)`)
	matches := uuidRegex.FindStringSubmatch(netJson.PayLoad)
	if len(matches) > 1 {
		uuid = matches[1]
	} else {
		UuidRegex := regexp.MustCompile(`Uuid: ([a-zA-Z0-9]+)`)
		tmpMatches := UuidRegex.FindStringSubmatch(netJson.PayLoad)
		if len(tmpMatches) > 1 {
			uuid = tmpMatches[1]
		}
	}
	t, err := time.Parse("2006-01-02 15:04:05.999999", netJson.TimeStamp)
	if err != nil {
		fmt.Println("Error parsing timestamp:", err)
		return err, nil
	}
	netData := NetLog{
		IPSrc:      netJson.IPSrc,
		PortSrc:    strconv.Itoa(netJson.PortSrc),
		IPDst:      netJson.IPDst,
		PortDst:    strconv.Itoa(netJson.PortDst),
		SeqNum:     netJson.SeqNum,
		AckNum:     netJson.AckNum,
		PayLoadLen: netJson.PayLoadLen,
		Method:     method,
		Time:       int64(t.UnixMicro()),
		UUID:       uuid,
	}
	return nil, &netData
}
