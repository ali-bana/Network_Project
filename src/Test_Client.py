from tools.simpletcp.clientsocket import ClientSocket



clientSock = ClientSocket('localhost', 8888, 1024, False)
clientSock.send("ali\n")
clientSock.send("ls")
clientSock.send("k")