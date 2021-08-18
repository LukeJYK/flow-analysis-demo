#!/usr/bin/python
#encoding:utf-8
import dpkt
import socket
import datetime
def printPcap(pcap):
    try:
        for timestamp, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf) #获得以太包，即数据链路层包
            print("ip layer:"+eth.data.__class__.__name__) #以太包的数据既是网络层包
            print("tcp layer:"+eth.data.data.__class__.__name__) #网络层包的数据既是传输层包
            print("http layer:" + eth.data.data.data.__class__.__name__) #传输层包的数据既是应用层包
            print('Timestamp: ',str(datetime.datetime.utcfromtimestamp(timestamp))) #打印出包的抓取时间
            if not isinstance(eth.data, dpkt.ip.IP):
                print('Non IP Packet type not supported %s' % eth.data.__class__.__name__)
            continue
        ip = eth.data
        do_not_fragment =bool(ip.off & dpkt.ip.IP_DF)
        more_fragments =bool(ip.off & dpkt.ip.IP_MF)
        fragment_offset = ip.off & dpkt.ip.IP_OFFMASK
        print('IP: %s -> %s (len=%d ttl=%d DF=%d MF=%d offset=%d)' % (socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), ip.len, ip.ttl, do_not_fragment, more_fragments,fragment_offset))
    except:
        pass

def main():
    f =open('demo.pcap','rb')
    pcap = dpkt.pcap.Reader(f)
    printPcap(pcap)

main()