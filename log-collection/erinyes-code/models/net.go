package models

import "erinyes/helper"

type Net struct {
	ID         int    `gorm:"primaryKey;column:id"`
	SrcID      int    `gorm:"column:src_id"`
	DstID      int    `gorm:"column:dst_id"`
	Method     string `gorm:"column:method"`
	Payload    string `gorm:"column:payload"`
	PayloadLen int    `gorm:"column:payload_len"`
	SeqNum     int64  `gorm:"column:seq_num"`
	AckNum     int64  `gorm:"column:ack_num"`
	Time       int64  `gorm:"column:time"`
	UUID       string `gorm:"column:uuid"`
}

func (Net) TableName() string {
	return "net"
}

func (n Net) EdgeName() string {
	return helper.AddQuotation(n.Method)
	//return helper.AddQuotation(n.Method + "_" + n.UUID)
}
func (n Net) HasEdgeUUID() bool {
	if n.UUID != "" {
		return true
	}
	return false
}

func (n Net) GetUUID() string {
	return n.UUID
}
