import socket
import sys,os
import threading
from threading import Thread
import datetime
BUFFER_SIZE = 1
HEADER_SIZE = 8
arg_size = len(sys.argv)
server_port = int(sys.argv[arg_size-3])
MSS = int(sys.argv[arg_size-1]) - HEADER_SIZE
server_ip = []
c_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
filename = sys.argv[arg_size-2]
loc = os.path.dirname(sys.argv[0])
dataPacket = '0101010101010101'
sendData = ''
for i in range(1,arg_size-3):
	server_ip.append(sys.argv[i])


def rdt_send(offset):
        f=open(loc+'\\'+filename+'.txt','rb')
        f.seek(offset)
        l=f.read(BUFFER_SIZE)	
        if(l):
                return l
        else:
                return b''
        f.close()
                
def carry_around_add(a, b):
    """Helper function for checksum function"""
    c = a + b
    return (c & 0xffff) + (c >> 16)


def checksum(msg):
    """Compute and return a checksum of the given data"""
    # Force data into 16 bit chunks for checksum
    if (len(msg) % 2) != 0:
        msg += "0".encode('utf-8')

    s = 0
    for i in range(0, len(msg), 2):
        w = msg[i] + ((msg[i+1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff
        
                

class peerThread(threading.Thread):
        def __init__(self,data,server_addr):
                threading.Thread.__init__(self)
                self.lock=threading.Lock()
                self.server_addr = server_addr
                self.data = data
        def run(self):
                c_sock.sendto(self.data,self.server_addr)
                            
                        
threads=[]



file_size = os.stat(loc+'\\'+filename+'.txt').st_size
remaining_size = file_size
offset = 0
count = 0


segment_no = 0
startTime = datetime.datetime.now()
while(remaining_size>=0):
        ackList = list(server_ip)
        ackCount = 0
        local_buffer=b''
        print('Remaining size:',remaining_size)
        while(len(local_buffer)<=MSS):
                tmp=rdt_send(offset)
                if((len(tmp)==1) and (len(local_buffer)<MSS)):
                        local_buffer=local_buffer.__add__(tmp)
                
                elif((len(tmp)<1) and (len(local_buffer)<MSS)):
                        local_buffer.__add__(tmp)
                        binSegNo = '{0:032b}'.format(segment_no)
                        check = checksum(local_buffer)
                        binaryCheck = '{0:016b}'.format(check)
                        sendData = binSegNo.encode('utf-8') + binaryCheck.encode('utf-8') + dataPacket.encode('utf-8') + local_buffer
                        count+=1
                        for ip_addr in server_ip:
                                server_addr = (ip_addr, server_port)
                                new_peer=peerThread(sendData,server_addr)
                                new_peer.start()
                                threads.append(new_peer)
                        for t in threads:
                            t.join()

                        while(ackCount!=len(server_ip)):
                            c_sock.settimeout(0.05)
                            try:
                                ack,address = c_sock.recvfrom(MSS)
                                serverSeqno = int(ack[0:32],2)
                                if(serverSeqno == segment_no):
                                    if(address[0] in ackList):
                                        ackCount+=1
                                        ackList.remove(address[0])

                            except socket.timeout:
                                print('Timeout, Sequence number = ', segment_no)
                                for ip_addr in ackList:
                                    server_addr = (ip_addr, server_port)
                                    new_peer=peerThread(sendData,server_addr)
                                    new_peer.start()
                                    threads.append(new_peer)
                                for t in threads:
                                    t.join()
                                continue
                                        
                        str=''
                        binSegNo = '{0:032b}'.format(segment_no)
                        binaryCheck = '{0:016b}'.format(0)
                        sendData = binSegNo.encode('utf-8') + binaryCheck.encode('utf-8') + dataPacket.encode('utf-8') + str.encode('utf-8')
                        for ip_addr in server_ip:
                                server_addr = (ip_addr, server_port)
                                new_peer=peerThread(sendData,server_addr)
                                new_peer.start()
                                threads.append(new_peer)
                        for t in threads:
                            t.join()

                        break
                else:
                    break
                
                offset = offset + BUFFER_SIZE
                if((len(tmp)==1) and (len(local_buffer)==MSS)):
                        binSegNo = '{0:032b}'.format(segment_no)
                        check = checksum(local_buffer)
                        binaryCheck = '{0:016b}'.format(check)
                        sendData = binSegNo.encode('utf-8') + binaryCheck.encode('utf-8') + dataPacket.encode('utf-8') + local_buffer
                        count+=1
                        
                        for ip_addr in server_ip:
                                server_addr = (ip_addr, server_port)
                                new_peer=peerThread(sendData,server_addr)
                                new_peer.start()
                                threads.append(new_peer)

                        for t in threads:
                            t.join()
						
                        while(ackCount!=len(server_ip)):
                            c_sock.settimeout(0.05)
                            try:

                                ack,address = c_sock.recvfrom(MSS)
                                serverSeqno = int(ack[0:32],2)
                                if(serverSeqno == segment_no):
                                    if(address[0] in ackList):
                                        ackList.remove(address[0])
                                        ackCount+=1

                            except socket.timeout:
                                print('Timeout, Sequence number = ', segment_no)
                                for ip_addr in ackList:
                                    server_addr = (ip_addr, server_port)
                                    new_peer=peerThread(sendData,server_addr)
                                    new_peer.start()
                                    threads.append(new_peer)
                                for t in threads:
                                    t.join()
                                continue
							
                                
                                
        if(segment_no == 1):
                segment_no = 0

        else:
                segment_no += 1
        remaining_size = remaining_size - MSS
                

endTime = datetime.datetime.now()
print('Time taken to transmit the file:', (endTime-startTime))