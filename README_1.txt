Point to Multipoint File Transfer Protocol using Stop and Wait ARQ mechanism. 

There are two files p2mpclient.py and p2mpserver.py. 

The server program takes the following arguments in the specified order: Port Number, File_name, Error Probability

Example: p2mpserver.py 7735 recv_file 0.05

The client takes the following command line arguments in the specified order: Server IP Addresses, Server port number, Maximum Segment Size.

Example: p2mpclient.py 192.168.1.2 192.168.1.12 7735 one_mb_test 500