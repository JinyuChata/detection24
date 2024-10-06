package main

import (
	"bufio"
	"fmt"
	parser_local "github.com/JinyuChata/alastor/parser-local"
	"os"
	"testing"
)

func TestParseStrace(t *testing.T) {
	parser := parser_local.NewStraceParser()

	parser.RegisterAllSyscallHook(func(msg *parser_local.StraceMessage) {
		fmt.Printf("Strace: %#v \n", msg)
	})

	file, err := os.Open("static/log/iterproduct-purchase-8555c6cc8d-fjpps/request.alastor.20")
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	reader := bufio.NewReader(file)
	parser.StartParse(reader)

}

func TestParseReqHandler(t *testing.T) {
	parser := parser_local.NewReqHandlerParser()

	parser.RegisterAllReqHook(func(msg *parser_local.ReqHandlerMessage) {
		fmt.Printf("Req Handler: %#v \n", msg)
	})

	file, err := os.Open("static/log/iterproduct-purchase-8555c6cc8d-fjpps/request.alastor.r.log")
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	reader := bufio.NewReader(file)
	parser.StartParse(reader)

}
