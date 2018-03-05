import socket,sys
from random import *

MSS = 556
serverPort = int(sys.argv[1])
filename = sys.argv[2]
prob = float(sys.argv[3])
print('server running')
serverSeqno = 0    #The sequence number of the next packet that the server is expecting
ackPacket = '1010101010101010'
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
serverSocket.bind(('', serverPort))
file = open(filename+'.txt', 'w')

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



data, address = serverSocket.recvfrom(MSS)
clientSeqno = int(data[0:32],2)   #Retrieving the sequence number of the packet the client has sent
clientChecksum = int(data[32:48],2)   #Retrieving the checksum as sent by the client
previous_checksum = 0
previous_seqno = 0
message = data[64:]

if(serverSeqno == clientSeqno):   #If the client has sent the packet that the server is expecting
        r = random()              #To induce error
        if(r>prob):
                serverChecksum = checksum(message)    
                if(clientChecksum == serverChecksum):  
                        binSegNo = '{0:032b}'.format(serverSeqno)
                        sendAck = binSegNo + '{0:016b}'.format(0) + ackPacket
                        serverSocket.sendto(sendAck.encode('utf-8'),address)
                        file.write(message.decode('utf-8'))
                        if(serverSeqno == 1):   #Sequence number is updated
                                serverSeqno = 0
                        else:
                                serverSeqno +=1
        else:
                print('Packet Loss, sequence number = ',serverSeqno)
                



while(data):
    
    data, address = serverSocket.recvfrom(MSS)
    clientSeqno = int(data[0:32],2)
    clientChecksum = int(data[32:48],2)
    message = data[64:]
    if(message.decode('utf-8') == ''):
        serverSocket.sendto("Last segment".encode('utf-8'),address)  
        file.write(message.decode('utf-8'))
        break
    else:
                if(serverSeqno == clientSeqno):
                        r = random()
                        if(r>prob):
                                serverChecksum = checksum(message)
                                previous_checksum = serverChecksum
                                if(clientChecksum == serverChecksum):
                                        binSegNo = '{0:032b}'.format(serverSeqno)
                                        sendAck = binSegNo + '{0:016b}'.format(0) + ackPacket
                                        serverSocket.sendto(sendAck.encode('utf-8'),address)
                                        file.write(message.decode('utf-8'))
                                        if(serverSeqno == 1):
                                                previous_seqno = 1
                                                serverSeqno = 0
                                        else:
                                                previous_seqno = 0										
                                                serverSeqno +=1
                                else:
                                        continue
                                        
                        else:
                                print('Packet Loss, sequence number = ',serverSeqno)
                else:
                        if(clientChecksum == previous_checksum):
                            binSegNo = '{0:032b}'.format(previous_seqno)
                            sendAck = binSegNo + '{0:016b}'.format(0) + ackPacket
                            serverSocket.sendto(sendAck.encode('utf-8'),address)
        
            
file.close()
print('file transfer successful')
serverSocket.close()
