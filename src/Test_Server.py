from tools.simpletcp.serversocket import ServerSocket

def callback(ip, queue, data):
    print(ip)
    print(queue)
    print(data)
    queue.put(bytes('dfgdhd', 'UTF-8'))



serversock = ServerSocket('localhost', 8888, callback, 1, 1024)
serversock.run()
