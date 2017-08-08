import socket,sys
import thread
import time
import os
import json
	
class Node:
	
	def __init__(self,serv_port,ID):#serv_port is the port that the node uses for serving requests, recv_port is used for receiving requests.
		self.neighbours = [] #Initialize the neighbours of the node to an empty list.
		self.neighbour_ping = []
		self.serv = serv_port
		self.host = socket.gethostname()
		self.id = ID 
		self.is_full = False
	
	
	def server_function(self):#Function to setup the server for a particular node.
		s = socket.socket()
		host = socket.gethostname()
		try:
			s.bind((host,self.serv))
		except:
			print("Connection already exists at this port. This port cannot be used.")
			os._exit(1)
		#Accept connections here
		s.listen(5)
		print("Server setup successfully. Waiting for connections...")
		while 1:
			c, addr = s.accept()	#Waits to accept a connection
			print 'Connected with ' + addr[0] + ':' + str(addr[1])
			#Start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
			thread.start_new_thread(self.client_thread ,(c,))	#Starts a new thread for every connection at the server.
		s.close()
		
		
	def client_function(self):
		time.sleep(2)	#Starts the client function 2 seconds after the server function starts. I am using two separate threads for client and server. So, I have kept a delay of 2 seconds to prevent overlap between these 2 functions.
		print("Available commands are:\n1)help\n2)open\n3)close\n4)info\n5)find\n6)get\n7)quit\nType'help' for details of the commands.")
		print "Host name is:"+str(socket.gethostname()+". Use this host name for opening connections")
		option = raw_input(">> ")
		while option != "quit":
			if option == "help":
				self.help()
			elif option == "open":
				host = raw_input("Enter host name: ")
				port = int(raw_input("Enter port to connect: "))
				thread.start_new_thread(self.open_connection,(host,port,))
				time.sleep(2)
			elif option == "close":
				id = raw_input("Enter the id of the host to close the connection: ")
				self.close(id)
			elif option == "info":
				self.info()
			elif option == "find":
				file_name = raw_input("Enter file name to find: ")
				self.find(file_name)
			elif option == "get":
				id = raw_input("Enter ID of file name to get: ")
				self.get(id)
			else:
				print("Invalid option")
			option = raw_input(">> ")
		os._exit(1)
		
	#Function for handling connections. This will be used to create threads
	def client_thread(self,c):
		c.send(self.id) #Sends the ID of the server node.
		#infinite loop so that function does not terminate and thread does not end.
		while True:		     
		    #Receiving data from client
		    data = c.recv(1024)
		    if data == "Get_neighbours":#Receives a message to send its neighbours.
		    	json_data = json.dumps(self.neighbour_ping)
		    	c.send(json_data)#Responds by sending its neighbours.
		    elif data == "Get_file_list":#Receives a Query
		    	file_name = c.recv(1024)
		    	list_of_files = os.listdir(self.id)
		    	final_list = []
		    	for item in list_of_files:
		    		print "File name:"+str(file_name)
		    		print "Item:" +str(item)
		    		print item.find(file_name)
		    		if item.find(file_name) != -1:
		    			final_list.append(item)
		    	for i in range(0,len(final_list)):
		    		final_list[i] = self.host+','+str(self.serv)+','+final_list[i]
		    	json_data = json.dumps(final_list)
		    	c.send(json_data)#Responds with a Query Hit
		    elif data == "Download_file":#Receives a request to download file.
		    	c.send("Which file do u want to download?")
		    	file_name = c.recv(1024)
		    	list_of_files = os.listdir(self.id)
		    	if file_name not in list_of_files:
		    		c.send("No such file found")
		    	else:
		    		f = open(self.id+'/'+file_name,'rb')
		    		print("Sending..")
		    		l = f.read(1024)
		    		while(l):
		    			c.send(l)
		    			l = f.read(1024)
		    		c.shutdown(socket.SHUT_WR)
		    		f.close()
		    		print("Done sending")
		    		break
		    elif not data: #The other connection is shutdown, so we end this connection.
		        break
		 
		#came out of loop
		c.close()
		print("Successfully closed connection.")
		
	def help(self):#Help function. Prints the details of various commands to console.
		print("Details of available commands:\n")
		print("help: Lists details of available commands\n")
		print("open(host): Connects to 'host'.\n")
		print("close(id): Closes connection by connection ID.\n")
		print("info: Lists the connected hosts with an ID for each host.\n")
		print("find(key): Searches files on the network and lists the results with an ID for each entry.\n")
		print("get(id): Download a file with the given ID.\n")
		print("Further details can be found in README\n")
		
	def open_connection(self,host,port):#Function to open a connection with the given host and port number. The host here should have the host name.
		print("Opening Connection...")
		for item in self.neighbours:
			if item[0] == host and item[1] == port:
				print("Already connected")
				return
		s = socket.socket()
		try:
			s.connect((host,port))
			host_id = s.recv(1024)
			self.neighbours.append((host,port,host_id,s))
			self.neighbour_ping.append((host,port))
			print("Connection opened successfully")
		except:
			print("Connection failed")
		thread.start_new_thread(self.add_2nd_neighbours,())	#Starts a new thread to add neighbours of neighbours using PING.
		
	def add_2nd_neighbours(self):
		print("Adding 2nd neighbours...")
		
		second = []
		for item in self.neighbours:
			second += self.get_2nd_neighbours(item[0],item[1])#Get the neighbours of neighbours
		if len(second) > 5:
			second = second[:5]	#Consider atmost 5 neighbours of neighbours to PING. This can be implemented to have a random choice.
		for item in second:
			thread.start_new_thread(self.ping,(item[0],item[1]))#PING the neighbours of neighbours.
		while 1:
			pass
			
	def get_2nd_neighbours(self,host,port):
		for item in self.neighbours:
			if item[0] == host and item[1] == port:
				item[3].send("Get_neighbours")
				json_string = item[3].recv(1024)
				neighbour_data = json.loads(json_string)
				break
		return neighbour_data #The second neighbours of the node.
			
	def ping(self,host,port):
		print("Pinging: "+str(host)+str(port))
		print("Opening Connection...")
		for item in self.neighbours:
			if item[0] == host and item[1] == port:
				print("Already connected")
				return
		s = socket.socket()
		try:
			s.connect((host,port))#Tries to PING.
			host_id = s.recv(1024) #This is like a received PONG.
			self.neighbours.append((host,port,host_id,s))
			self.neighbour_ping.append((host,port))
			print("Connection opened successfully with: "+str(host)+str(port))
		except:
			print("Could not connect with: "+str(host)+str(port))
			
	def close(self,id):#Closing connection with a host of given ID.
		flag = 0
		for item in self.neighbours:
			if item[2] == id:
				flag = 1
				break
		if flag == 1:
			self.neighbours.remove(item)
			for element in self.neighbour_ping:
				if item[0] == element[0] and item[1] == element[1]:
					flag = 1
					break
			self.neighbour_ping.remove(element)
			item[3].shutdown(socket.SHUT_WR)
			item[3].close()
			print("Successfully closed connection.")
		else:
			print("Error! Host with entered ID not found.")
			
	def info(self):#Info of nodes directly connected with the particular node.
		if not self.neighbours:
			print("Not connected to any host")
		else:
			for item in self.neighbours:
				print ("Host name: "+str(item[0])+", Port no.: "+str(item[1])+", Host ID: "+str(item[2]))
				
				
	def find(self,file_name):#Finds the file with name file_name. Matches upto a substring. Currently, case-sensitive.
		hop = 0	#The HOP parameter. 
		check_list = self.neighbour_ping
		file_list = []
		while hop!=5 and check_list:#Checks upto HOP=5, means the shortest path in the graph between the current node and the node at which file is checked is atmost 5.
			new_list = []
			for item in check_list:
				file_list= file_list+self.get_file_list(item,file_name)
				n = self.get_neighbour(item[0],item[1])
				new_list += n
			check_list = new_list
			hop += 1
		file_list = set(file_list)#Remove duplicates.
		if file_list:
			for item in file_list:
				split = item.split(',')
				print "File name:"+split[2]+", ID:"+item	#Print all file names with IDs
		else:
			print("No such files found")	#If no files are found, print this line.
			
	def get_file_list(self,item,file_name):#Gets the file list matching the file_name at a particular node upto a substring(case-sensitive) 
		flag = 0
		for node in self.neighbours:
			if item[0] == node[0] and item[1] == node[1]:
				flag = 1
				break
		if flag == 1:
			node[3].send("Get_file_list")
			node[3].send(file_name)
			file_list = node[3].recv(1024)
			file_list = json.loads(file_list)
		else:
			s = socket.socket()
			s.connect((item[0],item[1]))
			id_of_host = s.recv(1024)
			s.send("Get_file_list")
			s.send(file_name)
			file_list = s.recv(1024)
			file_list = json.loads(file_list)
			s.shutdown(socket.SHUT_WR)
			s.close()
		return file_list#Returns the fiel list.
			
	def get_neighbour(self,host,port):#Get neighbour list of a particular node, so that we can expand our search for the file until HOP parameter is reached.
		flag = 0
		for node in self.neighbours:
			if host == node[0] and port == node[1]:
				flag = 1
				break
		if flag == 1:
			node[3].send("Get_neighbours")
			n_list = node[3].recv(1024)
			n_list = json.loads(n_list)
		else:
			s = socket.socket()
			s.connect((host,port))
			id_of_host = s.recv(1024)
			s.send("Get_neighbours")
			n_list = s.recv(1024)
			n_list = json.loads(n_list)
			s.shutdown(socket.SHUT_WR)
			s.close()
		return n_list#Returns the list of neighbours.
		
		
	def get(self,id):#Download a file with the given ID.
		split_id = id.split(',')
		split_id[1] = int(split_id[1])
		flag = 0
		for item in self.neighbours:
			if split_id[0] == item[0] and split_id[1] == item[1]:
				flag = 1
		try:
			s = socket.socket()
			s.connect((split_id[0],split_id[1]))
			host_id = s.recv(1024)
			s.sendall("Download_file")
			mesg = s.recv(1024)
			s.sendall(split_id[2])
			f = open(self.id+'/'+split_id[2],'wb')
			l = s.recv(1024)
			if l != "No such file found":
				while(l):
					f.write(l)
					l = s.recv(1024)
				f.close()
				print("File received")
			else:
				print("Please enter a correct ID")
			s.shutdown(socket.SHUT_WR)
			s.close()
		except:
			print("Download failed")		
