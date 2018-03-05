There are three files - RS_Server, RFC_Server, RFC_Client
OS Platform Used : Windows

Execute all the programs in the command prompt. Relative File path has been given, hence do not include 'python' while executing

Steps to follow:

RS_Server: 
Execute it from the command prompt. 
1. Start the RS_Server before executing any other program.
2. No input from the user is needed to execute.
3. Command to Execute from command prompt - RS_Server.py


RFC_Client:

1.This file acts as client to both RS Server and to any other Peer Server. Depending on to which the peer is acting as client, the implementation differs.
2.When it acts as a client to RS Server, the second argument is its own RFC server's port number. 
For Eg: RFC_Client.py 9999 implies that the peer's RFC server is listening on port 9999.
3.When it is a client to a peer server, the second argument is the port number of the RFC server to which it wishes to connect.
For Eg: RFC_Client.py 50000 implies that it wants to connect to a peer server that is listening on port 50000
4.The program then prompts the user to enter the peer's hostname. Make sure that the peer's name starts with lowercase like peer0, peer1 etc.
5.Then the user should enter to which server it is connecting to. Enter 1 for connecting to RS server and 2 for connecting to Peer/RFC server.
6.The user will now be prompted to enter the message type depending on to which it has connected to. 
When it has connected to RS Server, one of the following message types should be given as input: Register, PQuery, Leave, KeepAlive
When it has connected to Peer Server, one the following message types should be given as input: RFCQuery, GetRFC
7.If the user has entered GetRFC as the message type, then the rfc number (only the number) that the user wishes to download should be entered next. 
8. Command to Execute from command prompt - RFC_Client.py 65401

RFC_Server:

1. The server should be up and running before any RFC_Client program is executed.
2. The second argument is its own port number and the third argument is its host name. 
For eg: "RFC_Server.py 65401 peer1" implies that peer1 is the RFC server listening on port 65401
3. Command to Execute from command prompt - RFC_Server.py 65401 peer1

RFC_Files:
 This is the local filespace that we created to store the RFC Files. We use six different folders named peer0,peer1...peer5 to hold the RFC Files and the
RFCIndex information. We have attached a empty structure along with the project code. Use these locations to store the RFC Files and the RFC_index information
in the "rfc_index.csv" file
