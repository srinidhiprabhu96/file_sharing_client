###########       README for using the program #################

This is developed by Srinidhi Prabhu, IIT Madras in May 2016.


The program is written in Python.

Every node is started by running the file main.py separately. For example, if you want to start 3 separate nodes, type "python main.py" in 3 separate terminals.

This will ask the ID of each node and the port on which the server for the particular node has to be setup. After the parameters are entered, the server will be setup. A message will be displayed if the setup of the server is successful.

For every new ID of the node, a folder is created. This folder will contain all the files shared/received through the network. Any files to be shared should be placed in this folder.

The list of files in the folder for that node are listed.

Next, the HOST NAME of the current system will be displayed. This HOST NAME is necessary to open connections.

Then, a prompt appears. You can enter the desired command here.

Assumption: All connections are directed. That is, if node 1 is connected to node 2(using function open), node 2 need not be connected to node 1.

############################### COMMANDS ##################################

1) help: Type 'help' for more information on the commands.

2) open: When this command is entered, it asks for the HOST NAME and the port number to connect. The HOST NAME is the HOST NAME of the node you want to connect to. The HOST NAME is defined above. If the connection is successful, the message is displayed. Moreover, the node starts searching/pinging for second neighbours in the network and connects to them, if necessary.

3) info: Type info to get the list of all nodes to which the current node is directly connected.

4) close: This closes a connection. Using the info command, find the ID of the node to which you want to close the connection. Then, provide this ID for closing the connection.

5) find: This searches for the given file name among nodes in the network. The search is done as follows: First, it searches for the files in the immediate neighbours, then checks the files among the neighbours of neighbours. This continues until the shortest directed path between the nodes is atmost 5. The files are matched upto a substring and the matched files are listed by ID.

6) get:  Gets a file by ID. Entering the ID will start a new connection, receive the file and close this connection.

7) quit: Quits the program. However, this may leave some ports still in use.

###########################################################################

Every file ID is of the form 'host_name,port,file_name'

Some errors such as socket already running on a given port have not been handled.

Some parts of code can be improved. For example, instead of taking the first five second neighbours to PING, we could choose a random set of five neighbours.

Matching of files is case-sensitive. This file-matching can be improved.

