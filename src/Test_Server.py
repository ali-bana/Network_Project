from src.Stream import Stream

def callback(address, data):
    print(address[0])
    print(address[1])
    print(data)




s = Stream('localhost', 8888, callback)

