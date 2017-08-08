from classes import Node
import socket
import thread
import time
import os
#n = Network()
user = raw_input("Enter your ID: ")
port = int(raw_input("Enter the port number you want to use: "))
curr_node = Node(port,user)
if not os.path.exists(user):
	os.makedirs(user)

print "List of files available to share: " + str(os.listdir(user))
thread.start_new_thread(curr_node.server_function,())
thread.start_new_thread(curr_node.client_function,())
		
while 1:#Infinite loop to prevent the program from closing
	pass
