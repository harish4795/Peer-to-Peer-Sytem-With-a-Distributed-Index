import socket
import threading
import csv
import time
import pickle
import sys,os
from threading import Thread
from socketserver import ThreadingMixIn
from datetime import datetime
import platform
import random

Host = ''
port = int(sys.argv[1])
host_name= sys.argv[2]
BUFFER_SIZE=2048
TTL_TIME=30
loc = os.path.dirname(sys.argv[0])+'\\RFC_Files\\'+host_name
print(loc)

class TTLThread(Thread):
	def __init__(self, ttl):
		Thread.__init__(self)
		self.ttl = ttl

	def run(self):
        while(self.ttl):
			time.sleep(1)
			self.ttl=self.ttl-1
			print('ttl:',self.ttl)
		
class peerThread(threading.Thread):
	def __init__(self,socket,clientIP):
		threading.Thread.__init__(self)
		self.lock=threading.Lock()
		print(self.lock)
		self.csocket=socket
		self.ip=clientIP[0]
		self.socket=clientIP[1]

		
	def run(self):
		print("Received connection request from:" + threading.currentThread().getName())
		getMessage = self.csocket.recv(BUFFER_SIZE).decode('utf-8')
		print('From Client\n',getMessage)
		if 'GetRFC' in getMessage:   #This block gets executed if the client peer requests for an RFC File. 
			keep_Alive = getMessage[getMessage.index('KEEP_ALIVE ')+11:]
			rfc_no= getMessage[getMessage.index('RFC_NO ')+7:getMessage.index(' <cr> <lf>\nKEEP_ALIVE')]  #Extracts the RFC no that the client peer has requested for
			filename='rfc'+rfc_no+'.txt'
			try:
				f=open(loc+'\\'+filename,'rb')
			except:
				print('Unable to open file.Error')
				self.csocket.close()
			fileSize = os.stat(loc+'\\'+filename).st_size
			sendMessage = 'POST RFC Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) + '<cr> <lf>\nContent Length ' + str(fileSize)
			self.csocket.send(sendMessage.encode('utf-8'))
			print(sendMessage)
			self.csocket.recv(BUFFER_SIZE).decode('utf-8')
			l=f.read(BUFFER_SIZE)
			while(fileSize>0):
				self.csocket.send(l)   
				fileSize = fileSize - BUFFER_SIZE
				l=f.read(BUFFER_SIZE)
				if((fileSize==0) or (fileSize<0)):
					f.close()
			
			while(keep_Alive == 'True'):  #Keep Alive is set to True if the client peer wants to receive multiple RFCs over a single TCP connection 
					print('waiting for rfc_no')
					getMessage = self.csocket.recv(BUFFER_SIZE).decode('utf-8')
					rfc_no= getMessage[getMessage.index('RFC_NO ')+7:getMessage.index(' <cr> <lf>\nKEEP_ALIVE')]
					keep_Alive = getMessage[getMessage.index('KEEP_ALIVE ')+11:]
					filename='rfc'+rfc_no+'.txt'
					try:
						f=open(loc+'\\'+filename,'rb')
					except:
						print('Unable to open file.Error')
						self.csocket.close()
					fileSize = os.stat(loc+'\\'+filename).st_size
					sendMessage = 'POST RFC Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) + '\nContent Length ' + str(fileSize)
					self.csocket.send(sendMessage.encode('utf-8'))
					print(sendMessage)
					self.csocket.recv(BUFFER_SIZE).decode('utf-8')
					l=f.read(BUFFER_SIZE)
					while(fileSize>0):
						self.csocket.send(l)
						fileSize = fileSize - BUFFER_SIZE
						l=f.read(BUFFER_SIZE)
						if((fileSize==0) or (fileSize<0)):
							f.close()
				
			self.csocket.close()
			print('finished sending all files')
		elif 'RFCQuery' in getMessage:   #This block gets executed if the client peer wants to know the list of RFCs that the server peer has. 
			myRFCIndex=RFCList()
			with open(loc+'\\index_list.csv','r') as f:
				reader=csv.reader(f)
				for row in reader:
					index=RFCIndex(row[0],row[1],row[2])
					myRFCIndex.add(index)
			f.close()
				
			if(myRFCIndex.head!=None):
				sendMessage = 'POST RFCQuery Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
				print(sendMessage)
				self.csocket.send(sendMessage.encode('utf-8'))
				self.lock.acquire()
				self.csocket.send(pickle.dumps(myRFCIndex,pickle.HIGHEST_PROTOCOL))
				self.lock.release()
				self.csocket.close()
			else:
				sendMessage = 'POST RFCQuery NOT Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
				print(sendMessage)
class RFCIndex:
	def __init__(self,no=None,title_name=None,host_name=None):
		self.rfc_no=no
		self.title=title_name
		self.hostname=host_name
		if((self.hostname==None) or (self.hostname==host_name)):
			self.TTL=7200
		else:
			self.TTL=TTLThread(TTL_TIME)
				
	def getrfc_no(self):
		return self.rfc_no
	def gettitle(self):
		return self.title
	def gethostname(self):
		return self.hostname


class RFCNode:
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
		print('index added to linkedList')
	
	def show(self):
		tmp=self.head
		while(tmp!=None):
			index=tmp.getNode()
			print(index.rfc_no,index.title,index.hostname)
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


serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((Host,port))
threads=[]
ttlthreads=[]

			
while True:
	serverSocket.listen(6)
	print('listening')
	clientSocket, clientIP=serverSocket.accept()
	print(clientSocket)
	print(clientIP)
	new_peer=peerThread(clientSocket,clientIP)   #New thread gets created for each connection from the client peer. 
	new_peer.start()
	threads.append(new_peer)        

for t in threads:
	t.join()