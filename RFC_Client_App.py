import socket,pickle
import pprint,ast,os
import sys
import time
import csv
from datetime import datetime
import platform
import random

serverHost ='127.0.0.1'
BUFFER_SIZE = 2048
print('enter your hostname')
hostname = input()
loc = os.path.dirname(sys.argv[0])+'\\RFC_Files\\'+hostname
class Peer:
	def __init__(self, host=None, port=None, cookie=None):
		self.hostname = host    
		self.port = port
		self.cookie = cookie

class RSPeer:
	def __init__(self,host=None,port=None):
		self.host=host
		self.port=port
	
class PeerNode:
	def __init__(self,obj:RSPeer):
		self.peer_obj=obj
		self.next=None
	
	def getpeer_obj(self):
		return self.peer_obj

	def getNext(self):
		return self.next

	def setpeer_obj(self,obj:RSPeer):
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
		print('add to linkedlist successful')
		
	def show_nodes(self):
		tmp=self.head
		while(tmp!=None):
			peer_obj=tmp.getpeer_obj()
			print(peer_obj.hostname,peer_obj.port)
			tmp=tmp.getNext()

class RFCIndex():
	def __init__(self,rfc_no=None,title=None,hostname=None):
		self.rfc_no=rfc_no
		self.title=title
		self.hostname=hostname

class RFCNode():
	def __init__(self,obj:RFCIndex):
		self.rfc_node=obj
		self.next=None
	
	def getNode(self):
		return self.rfc_node
	
	def setNode(self,obj:RFCIndex):
		self.rfc_node=obj

	def getNext(self):
		return self.next
	
	def setNext(self,newNext):
		self.next=newNext
		
class RFCList:
	def __init__(self):
		self.head=None
	
	def add(self,index):
		tmp=RFCNode(index)
		tmp.setNext(self.head)
		self.head=tmp
	
	def show(self):
		tmp=self.head
		while(tmp!=None):
			index=tmp.getNode()
			print(index.rfc_no,',',index.title,',',index.hostname)
			tmp=tmp.getNext()
			
	def delete(self,index):
		tmp=self.head
		previous=None
		found=False
		while not found:
			rfc_index=tmp.getNode
			if(rfc_index == index):
				found=True
			else:
				previous=tmp
				tmp=tmp.getNext()
		if(previous==None):
			self.head=tmp.getNext()
		else:
			previous.setNext(tmp.getNext())
	
	def write_csv(self):
		dup = check_dup(self,loc)
		tmp=self.head
		
		with open(loc+'\\index_list.csv','a') as f:
			while(tmp!=None):
				index=tmp.getNode()
				if(len(dup)==0):
					row= index.rfc_no+','+index.title+','+index.hostname+'\n'
					f.write(row)
				else:
					if(index.hostname in dup):
						print('Entry found')
					else:
						row= index.rfc_no+','+index.title+','+index.hostname+'\n'
						f.write(row)
							
				tmp=tmp.getNext()
		f.close()
		
def check_dup(objectRecv:RFCList,loc):
	list1=[]
	list2=[]
	dup=[]
	with open(loc+'\\index_list.csv','r') as f:
		reader=csv.reader(f)
		for row in reader:
			list1.append(row[2])

	f.close()
	tmp=objectRecv.head
	while(tmp!=None):
		index=tmp.getNode()
		list2.append(index.hostname)
		tmp=tmp.getNext()

	set1=set(list1)
	set2=set(list2)
	for p in list(set1):
		for i in range(len(list(set2))):
			if(p==list(set2)[i]):
				dup.append(p)
	return dup

def found_func(list:PeerList,host):
	tmp= list.head
	found=False
	if(tmp==None):
		print('No peer has Registered yet.')
	while tmp!=None:
		peer_obj=tmp.getpeer_obj()
		if(peer_obj.hostname==host):
			found=True
			tmp=tmp.getNext()
		else:
			tmp=tmp.getNext()
	return found

objectRecv=PeerList()
objectRecv1=RFCList()

print('Enter which server you want to connect to ? 1. RSServer 2.RFCServer of another Peer')
type=input()

if(type == '1'):
	HOST,PORT = 'localhost',65500
	client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_connection.connect((HOST,PORT))
	port= sys.argv[1]
	
	print('Enter the communication type 1.Register 2.PQuery 3.Leave 4.KeepAlive')
	messageType = input()
	
	file_name=hostname+'Cookie.txt'    #Cookie information is being maintained in a file
	try:
		file=open(file_name,'r')       
		peerInfo = ast.literal_eval(file.read())
		file.close()
		cookie = peerInfo.get('cookie','None')
		
	except IOError:
		cookie = 'None'
		if messageType == "Register":
			sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname +' <cr> <lf>\nPort ' + str(port) +' <cr> <lf>\nCookie '+ str(cookie) +' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n'
			print(sendMessage)
			client_connection.send(sendMessage.encode('utf-8'))
			try:    #The peer receives its cookie information only if it's registering for the first time. 
				P0 = Peer(hostname,port)
				recvMessage =(client_connection.recv(BUFFER_SIZE).decode('utf-8'))
				print('From Server\n', recvMessage)
				P0.cookie = int(recvMessage[recvMessage.index('cookie')+6:recvMessage.index('<cr> <lf>\nFrom')])
				print('Cookie information updated: Cookie is ', P0.cookie)
				print('Saving cookie in '+hostname+'Cookie.txt')
				attributes=vars(P0)
				file_name=hostname+'Cookie.txt'
				file=open(file_name,'w')
				file.write(pprint.pformat(attributes))
				file.close()
			except:   
				print('Already Registered and active')
				client_connection.close()
		if messageType == 'PQuery':
			sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname +' <cr> <lf>\nPort ' + str(port) +' <cr> <lf>\nCookie '+ str(cookie) +' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n'
			print(sendMessage)
			client_connection.send(sendMessage.encode('utf-8'))
			recvMessage =(client_connection.recv(BUFFER_SIZE).decode('utf-8'))
			print('From Server\n', recvMessage)
			try:   #The RS Server sends the list of active peers only if the requesting peer is currently active and has already registered.
				l_file = client_connection.makefile(mode='rb')
				objectRecv = pickle.load(l_file)
				l_file.close()
				if(objectRecv.head == None):
					print('No Peers other than you are active')
				else:
					print ('List of active peers\n')
					objectRecv.show_nodes()
			except:
				print('Peer not registered or left. Register to get PeerList')
				client_connection.close()
		if messageType == 'Leave':
			sendMessage = 'POST ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname +' <cr> <lf>\nPort ' + str(port) +' <cr> <lf>\nCookie '+ str(cookie) +' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n'
			print(sendMessage)
			client_connection.send(sendMessage.encode('utf-8'))
			try:
				recvMessage = (client_connection.recv(BUFFER_SIZE).decode('utf-8'))
				print('From Server\n',recvMessage)
				client_connection.close()
			except:
				print('Peer already left')
		if messageType == 'KeepAlive':
			sendMessage = 'POST ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname +' <cr> <lf>\nPort ' + str(port) +' <cr> <lf>\nCookie '+ str(cookie) +' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n'
			print(sendMessage)
			client_connection.send(sendMessage.encode('utf-8'))
			recvMessage = client_connection.recv(BUFFER_SIZE).decode('utf-8')
			print('From Server\n',recvMessage)
			client_connection.close()
elif(type == '2'):    #If the client peer wants to connect to an RFC server 
		serverPort = int(sys.argv[1])
		print('Connecting to RFCServer:',serverPort)
		clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientSock.connect((serverHost,serverPort))
		print('Enter your hostname')
		print('Enter the type of action: 1.RFCQuery  2.GetRFC')
		messageType = input()
		if messageType == 'RFCQuery':
			keep_Alive = False
			sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname + ' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\nKEEP_ALIVE ' + str(keep_Alive)
			print(sendMessage)
			clientSock.send(sendMessage.encode('utf-8'))
			recvMessage = clientSock.recv(BUFFER_SIZE).decode('utf-8')
			print('From Server\n', recvMessage)
			if('RFCQuery Found' in recvMessage):
				file=clientSock.makefile(mode='rb')
				objectRecv1 = pickle.load(file)
				print ('RFC Index sent by the server\n')
				objectRecv1.show()
				file.close()
				objectRecv1.write_csv()
			
		if messageType == 'GetRFC':
			print('enter rfc number to download')
			rfc_no=input()
			keep_Alive = False
			sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname + ' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>RFC_NO ' + rfc_no + ' <cr> <lf>\nKEEP_ALIVE ' + str(keep_Alive)
			print(sendMessage)
			clientSock.send(sendMessage.encode('utf-8'))
			filename='rfc'+rfc_no+'.txt'
			f = open(loc+'\\'+filename, 'wb')
			recvMessage = clientSock.recv(BUFFER_SIZE).decode('utf-8')
			print('From Server\n',recvMessage)
			fileSize = int(recvMessage[recvMessage.index('Content Length ')+15:])
			while(fileSize>0):
				print('receiving data...')
				data = clientSock.recv(BUFFER_SIZE)
				print('data=%s',data)
				f.write(data)
				fileSize = fileSize - BUFFER_SIZE
			f.close()
			print('Successfully got the file')
		clientSock.close()
	
else:
	print('thankyou')