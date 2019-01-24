from src.Stream import Stream
import time

def callback(address, data):
    print(address[0])
    print(address[1])
    print(data)


if __name__ == '__main__':

    s = Stream('localhost', 8888,)
    time.sleep(5)
    print('sdlkv')
    for p in s.read_in_buf():
        print(p)


