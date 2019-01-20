import threading
import time
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from src.Peer import Peer

class UI():
    def __init__(self):
        print('enter ip and port')
        ip = input()
        port = input()
        print("wich one? A fucking root or an asshole client?")
        s = input()
        if s == 'root':
            self.isRoot = True
            self.peer = Peer(ip, int(port), self.isRoot, self)
        else:
            self.isRoot = False
            print('enter server ip and port')
            rootIP = input()
            rootPort = input()
            self.peerv = Peer(ip, int(port), self.isRoot, self, (rootIP, rootPort))



        self.peer = Peer()

    def display_message(self, message):
        print(message)

    def display_pkt(self, pkt):
        print('header: ')
        print(pkt.get_header)
        print('body: ')
        print(pkt.get_body)
    def add_to_buffer(self, shit):
        self.peer_buffer.put(shit)






class InputReader(threading.Thread):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setDaemon(True)
    def run(self):
        while True:
            s = input()
            self.ui.add_to_buffer(s)



