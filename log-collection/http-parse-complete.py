from __future__ import print_function
from bcc import BPF
from sys import argv

import socket
import os
import binascii
import time
import json
from datetime import datetime

CLEANUP_N_PACKETS = 1024  # cleanup every CLEANUP_N_PACKETS packets received
MAX_URL_STRING_LEN = 8192  # max url string len (usually 8K)
MAX_AGE_SECONDS = 30  # max age entry in bpf_sessions map


# cleanup function
def cleanup():
    # get current time in seconds
    # current_time = int(time.time())
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    # looking for leaf having:
    # timestap  == 0        --> update with current timestamp
    # AGE > MAX_AGE_SECONDS --> delete item
    for key, leaf in bpf_sessions.items():
        try:
            current_leaf = bpf_sessions[key]
            # set timestamp if timestamp == 0
            if (current_leaf.timestamp == 0):
                bpf_sessions[key] = bpf_sessions.Leaf(current_time)
            else:
                # delete older entries
                if (current_time - current_leaf.timestamp > MAX_AGE_SECONDS):
                    del bpf_sessions[key]
        except:
            print("cleanup exception.")
    return


# args
def usage():
    print("USAGE: %s [-i <if_name>]" % argv[0])
    print("")
    print("Try '%s -h' for more options." % argv[0])
    exit()


# help
def help():
    print("USAGE: %s [-i <if_name>]" % argv[0])
    print("")
    print("optional arguments:")
    print("   -h                       print this help")
    print("   -i if_name               select interface if_name. Default is eth0")
    print("")
    print("examples:")
    print("    http-parse              # bind socket to eth0")
    print("    http-parse -i wlan0     # bind socket to wlan0")
    exit()


# arguments
interface = ""

if len(argv) == 2:
    if str(argv[1]) == '-h':
        help()
    else:
        usage()

if len(argv) == 3:
    if str(argv[1]) == '-i':
        interface = argv[2]
    else:
        usage()

if len(argv) > 3:
    usage()



# initialize BPF - load source code from http-parse-complete.c
bpf = BPF(src_file="http-parse-complete.c", debug=0)

# load eBPF program http_filter of type SOCKET_FILTER into the kernel eBPF vm
# more info about eBPF program types
# http://man7.org/linux/man-pages/man2/bpf.2.html
function_http_filter = bpf.load_func("http_filter", BPF.SOCKET_FILTER)

# create raw socket, bind it to interface
# attach bpf program to socket created
BPF.attach_raw_socket(function_http_filter, interface)

# get file descriptor of the socket previously
# created inside BPF.attach_raw_socket
socket_fd = function_http_filter.sock

# create python socket object, from the file descriptor
sock = socket.fromfd(socket_fd, socket.PF_PACKET,
                     socket.SOCK_RAW, socket.IPPROTO_IP)
# set it as blocking socket
sock.setblocking(True)

# get pointer to bpf map of type hash
bpf_sessions = bpf.get_table("sessions")

# packets counter
packet_count = 0

# dictionary containing association
# <key(ipsrc,ipdst,portsrc,portdst),payload_string>.
# if url is not entirely contained in only one packet,
# save the firt part of it in this local dict
# when I find \r\n in a next pkt, append and print the whole url
local_dictionary = {}
http_data = {}
try:
    while True:
        # retrieve raw packet from socket
        packet_str = os.read(socket_fd, 4096)  # set packet length to max packet length on the interface
        packet_count += 1

        # DEBUG - print raw packet in hex format
        # packet_hex = binascii.hexlify(packet_str)
        # print ("%s" % packet_hex)

        # convert packet into bytearray
        packet_bytearray = bytearray(packet_str)

        # ethernet header length
        ETH_HLEN = 14

        # IP HEADER
        # https://tools.ietf.org/html/rfc791
        # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |Version|  IHL  |Type of Service|          Total Length         |
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #
        # IHL : Internet Header Length is the length of the internet header
        # value to multiply * 4 byte
        # e.g. IHL = 5 ; IP Header Length = 5 * 4 byte = 20 byte
        #
        # Total length: This 16-bit field defines the entire packet size,
        # including header and data, in bytes.

        # calculate packet total length
        total_length = packet_bytearray[ETH_HLEN + 2]  # load MSB
        total_length = total_length << 8  # shift MSB
        total_length = total_length + packet_bytearray[ETH_HLEN + 3]  # add LSB

        # calculate ip header length
        ip_header_length = packet_bytearray[ETH_HLEN]  # load Byte
        ip_header_length = ip_header_length & 0x0F  # mask bits 0..3
        ip_header_length = ip_header_length << 2  # shift to obtain length

        # retrieve ip source/dest
        ip_src_str = packet_str[ETH_HLEN + 12: ETH_HLEN + 16]  # ip source offset 12..15
        ip_dst_str = packet_str[ETH_HLEN + 16:ETH_HLEN + 20]  # ip dest   offset 16..19

        ip_src = int(binascii.hexlify(ip_src_str), 16)
        ip_dst = int(binascii.hexlify(ip_dst_str), 16)


        # TCP HEADER
        # https://www.rfc-editor.org/rfc/rfc793.txt
        #  12              13              14              15
        #  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |  Data |           |U|A|P|R|S|F|                               |
        # | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
        # |       |           |G|K|H|T|N|N|                               |
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #
        # Data Offset: This indicates where the data begins.
        # The TCP header is an integral number of 32 bits long.
        # value to multiply * 4 byte
        # e.g. DataOffset = 5 ; TCP Header Length = 5 * 4 byte = 20 byte

        # calculate tcp header length
        tcp_header_length = packet_bytearray[ETH_HLEN + ip_header_length + 12]  # load Byte
        tcp_header_length = tcp_header_length & 0xF0  # mask bit 4..7
        tcp_header_length = tcp_header_length >> 2  # SHR 4 ; SHL 2 -> SHR 2

        # retrieve port source/dest
        port_src_str = packet_str[ETH_HLEN + ip_header_length:ETH_HLEN + ip_header_length + 2]
        port_dst_str = packet_str[ETH_HLEN + ip_header_length + 2:ETH_HLEN + ip_header_length + 4]
        seq_num = packet_str[ETH_HLEN + ip_header_length + 4:ETH_HLEN + ip_header_length + 8]
        ack_num = packet_str[ETH_HLEN + ip_header_length + 8:ETH_HLEN + ip_header_length + 12]

        port_src = int(binascii.hexlify(port_src_str), 16)
        port_dst = int(binascii.hexlify(port_dst_str), 16)
        seq_num = int(binascii.hexlify(seq_num), 16)
        ack_num = int(binascii.hexlify(ack_num), 16)

        # calculate payload offset
        payload_offset = ETH_HLEN + ip_header_length + tcp_header_length

        # payload_string contains only packet payload
        payload_string = packet_str[(payload_offset):(len(packet_bytearray))]
        # CR + LF (substring to find)
        crlf = b'\r\n'

        # current_Key contains ip source/dest and port source/map
        # useful for direct bpf_sessions map access
        current_Key = bpf_sessions.Key(ip_src, ip_dst, port_src, port_dst, seq_num, ack_num)
        ip_from = socket.inet_ntoa(int.to_bytes(ip_src, 4, byteorder='big'))
        ip_to = socket.inet_ntoa(int.to_bytes(ip_dst, 4, byteorder='big'))
        http_data["time_stamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        http_data["ip_src"] = ip_from
        http_data["port_src"] = port_src
        http_data["ip_dst"] = ip_to
        http_data["port_dst"] = port_dst
        http_data["sequence_num"] = seq_num
        http_data["acknowledge_num"] = ack_num
        http_data["payload_len"] = total_length - ip_header_length - tcp_header_length

        # looking for HTTP GET/POST request
        if ((payload_string[:3] == b'GET') or (payload_string[:4] == b'POST')
                or (payload_string[:4] == b'HTTP') or (payload_string[:4] == b'HEAD')):
            # match: HTTP GET/POST packet found
            if (crlf in payload_string):
                # url entirely contained in first packet -> print it all
                http_data["payload"] = payload_string.decode("utf-8", "ignore")
                try:
                    del bpf_sessions[current_Key]
                except:
                    print("error during delete from bpf map ")
            else:
                # url NOT entirely contained in first packet
                # not found \r\n in payload.
                # save current part of the payload_string in dictionary
                # <key(ips,ipd,ports,portd),payload_string>
                local_dictionary[binascii.hexlify(current_Key)] = payload_string
        else:
            # NO match: HTTP GET/POST  NOT found

            # check if the packet belong to a session saved in bpf_sessions
            if (current_Key in bpf_sessions):
                # check id the packet belong to a session saved in local_dictionary
                # (local_dictionary maintains HTTP GET/POST url not
                # printed yet because split in N packets)
                if (binascii.hexlify(current_Key) in local_dictionary):
                    # first part of the HTTP GET/POST url is already present in
                    # local dictionary (prev_payload_string)
                    prev_payload_string = local_dictionary[binascii.hexlify(current_Key)]
                    # looking for CR+LF in current packet.
                    if (crlf in payload_string):
                        # last packet. containing last part of HTTP GET/POST
                        # url split in N packets. Append current payload
                        prev_payload_string += payload_string

                        http_data["payload"] = prev_payload_string.decode("utf-8", "ignore")
                        # clean bpf_sessions & local_dictionary
                        try:
                            del bpf_sessions[current_Key]
                            del local_dictionary[binascii.hexlify(current_Key)]
                        except:
                            print("error deleting from map or dictionary")
                    else:
                        # NOT last packet. Containing part of HTTP GET/POST url
                        # split in N packets.
                        # Append current payload
                        prev_payload_string += payload_string
                        # check if not size exceeding
                        # (usually HTTP GET/POST url < 8K )
                        if (len(prev_payload_string) > MAX_URL_STRING_LEN):
                            http_data["payload"] = prev_payload_string.decode("utf-8", "ignore")
                            try:
                                del bpf_sessions[current_Key]
                                del local_dictionary[binascii.hexlify(current_Key)]
                            except:
                                print("error deleting from map or dict")
                        # update dictionary
                        local_dictionary[binascii.hexlify(current_Key)] = prev_payload_string
                else:
                    # first part of the HTTP GET/POST url is
                    # NOT present in local dictionary
                    # bpf_sessions contains invalid entry -> delete it
                    try:
                        del bpf_sessions[current_Key]
                    except:
                        print("error del bpf_session")
        print(json.dumps(http_data))
        http_data.clear()
        # check if dirty entry are present in bpf_sessions
        if (((packet_count) % CLEANUP_N_PACKETS) == 0):
            cleanup()
except KeyboardInterrupt:
    del local_dictionary
    del http_data
    bpf.close()
    quit()
