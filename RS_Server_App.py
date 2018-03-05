import socket
import pickle
import random
import time
from datetime import datetime
import platform

cookieList=[]
BUFFER_SIZE=2048
def setCookie():
	cookie = random.randint(1,50)  
	while(cookie in cookieList):
		cookie = random.randint(1,50)  #To generate unique cookie number for each peer
	cookieList.append(cookie)
	return cookie
	
class Peer:
        def __init__(self, host=None, port=None, cookie=None):
                self.hostname = host    
                self.port = port
                self.cookie = cookie
                if self.cookie == None:    
                    self.cookie = setCookie()    #Peer is registering for the first time, hence it has to obtain a cookie.
                    self.no_active = 0
                else:
                    self.cookie = cookie 
                    self.no_active = setInstance(self.hostname, myPeer_List)   #Updating the number of times the peer has been active 
                self.active_flag=True
                self.TTL = 7200
                self.recent_reg_dateTime = time.strftime("%H:%M:%S")

class PeerNode:
        def __init__(self,obj:Peer):
                self.peer_obj=obj
                self.next=None
	
        def getpeer_obj(self):
                return self.peer_obj

        def getNext(self):
                return self.next

        def setpeer_obj(self,obj:Peer):
                self.peer_obj=obj

        def setNext(self,newnext):
                self.next = newnext

class PeerList:
        def __init__(self):
                self.head=None
	
        def add(self,peer):
                tmp=PeerNode(peer)
                tmp.setNext(self.head)
                self.head=tmp
        def show_nodes(self):
                tmp=self.head
                while(tmp!=None):
                    peer_obj=tmp.getpeer_obj()
                    print(peer_obj.hostname,peer_obj.port,peer_obj.cookie,peer_obj.active_flag,peer_obj.TTL,peer_obj.no_active,peer_obj.recent_reg_dateTime)
                    tmp=tmp.getNext()
        def delete(self,host):
                tmp=self.head
                previous=None
                found=False
                while not found:
                    rfc_index=tmp.getpeer_obj()
                    if(rfc_index.hostname == host):
                        found=True
                    else:
                        previous=tmp
                        tmp=tmp.getNext()
                if(previous==None):
                    self.head=tmp.getNext()
                else:
                    previous.setNext(tmp.getNext())


def found_func(list:PeerList,host):   #This function checks if the peer has already registered. 
	tmp= list.head
	found=False
	while tmp!=None:
		peer_obj=tmp.getpeer_obj()
		if(peer_obj.hostname==host):
			found=True
			tmp=tmp.getNext()
		else:
			tmp=tmp.getNext()
	return found
def cmpPeerLists(list:PeerList,host):
	list1=PeerList()
	found=found_func(list,host)
	tmp=list.head
	while tmp!= None:
		peer_obj=tmp.getpeer_obj()
		if(found==True and peer_obj.active_flag==True):    #If the peer has registered and is active
			list1.add(peer_obj)
			tmp=tmp.getNext()
		elif(found==True and peer_obj.active_flag==False):    #If the peer has registered but is not active 
			tmp=tmp.getNext()
			
		else:
			tmp=tmp.getNext()
			
	list1.show_nodes()
	return list1


def setFlag(host, list:PeerList):
	list1=PeerList()
	tmp= list.head
	while tmp!= None:
		peer_obj=tmp.getpeer_obj()
		if(peer_obj.hostname == host):
			peer_obj.active_flag = False
			tmp=tmp.getNext()
		else:
			tmp=tmp.getNext()
		
	print(host + ' is now inactive\n')

def setInstance(host, list:PeerList):
        list1=PeerList()
        tmp= list.head
        while tmp!= None:
                peer_obj=tmp.getpeer_obj()
                if(peer_obj.hostname == host):
                        peer_obj.no_active+=1
                        tmp=tmp.getNext()
                        return peer_obj.no_active
                else:
                        tmp=tmp.getNext()
        return 0
	
        

HOST,PORT = '',65500
listen_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
listen_socket.bind((HOST,PORT))
listen_socket.listen(6)   #Max of 6 pending requests can be in the queue

myPeer_List=PeerList()
myactivePeer_List=PeerList()
tobesent=PeerList()
print('RS Server listening on PORT '+ str(PORT))

while True:
		client_connection,client_address=listen_socket.accept()
		getMessage = client_connection.recv(BUFFER_SIZE).decode('utf-8')
		Host = getMessage[getMessage.index('Host')+5:getMessage.index(' <cr> <lf>\nPort')]   #Extracts the Host information
		Port = getMessage[getMessage.index('Port')+5:getMessage.index(' <cr> <lf>\nCookie')] #Extracts the port number 
		Cookie = getMessage[getMessage.index('Cookie')+6:getMessage.index(' <cr> <lf>\nOperating')]  
        print('Received a request from ',Host)
		print('From Client\n',getMessage)
		if 'Register' in getMessage:
				if Cookie == ' None':   #Peer is registering for the first time
					peer_obj=Peer(Host, Port)
				else:
					peer_obj=Peer(Host, Port, Cookie)
       				myactivePeer_List=cmpPeerLists(myPeer_List,Host)
				if(found_func(myactivePeer_List,Host)== True):
					client_connection.close()    #Peer information need not be added to the linked list if it has already registered, hence closing the connection. 
				else:
					myPeer_List.add(peer_obj)   #Adding the peer information to the linked list. 
					print('Peer successfully registered with the server')
					print('sending cookie information to the peer')
					sendMessage = 'POST peer-cookie ' + str(peer_obj.cookie) +' <cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) +' <cr> <lf>\n'
					print(sendMessage)
					client_connection.send(sendMessage.encode('utf-8'))
					client_connection.close()
		elif 'PQuery' in getMessage:
				PQueryList=cmpPeerLists(myPeer_List,Host)
				if(found_func(PQueryList,Host)== True):   #To ensure that only currently active peers get the active peer list
  					PQueryList.delete(Host)               #The active peer list should not contain the host which has queried for it					
					sendMessage = 'POST PQuery Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
					print(sendMessage)
					client_connection.send(sendMessage.encode('utf-8'))
					client_connection.send(pickle.dumps(PQueryList,pickle.HIGHEST_PROTOCOL))   #Using pickle to send the linked list
				else:    
					sendMessage = 'POST PQuery Not Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
					print(sendMessage)
					client_connection.send(sendMessage.encode('utf-8'))
					client_connection.close()
		elif 'Leave' in getMessage:
				myactivePeer_List=cmpPeerLists(myPeer_List,Host)
				if(found_func(myactivePeer_List,Host)== True):
					setFlag(Host, myPeer_List)  #The active flag of the host is set to False
					sendMessage = 'POST Leave Successful<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
					print(sendMessage)
					client_connection.send(sendMessage.encode('utf-8'))
					client_connection.close()
				else:
					client_connection.close()
		elif  'KeepAlive' in getMessage:
				sendMessage = 'POST Update TTL Successful<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
				client_connection.send(sendMessage.encode('utf-8'))
				print(sendMessage)
