import threading
from src.Peer import Peer
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from src.tools.Node import Node
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
import sys


#

class UI:
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
            self.peer = Peer(ip, int(port), self.isRoot, self, (rootIP, rootPort))

        self.peer_buffer = self.peer.ui_buffer
        self.peer.start()
        self.reader = InputReader(self)
        self.reader.start()

    def display_message(self, message):
        print(message)

    def display_pkt(self, pkt):
        print('header: ')
        print(pkt.get_header())
        print('body: ')
        print(str(pkt.get_body()))

    def print_header(self, header):
        print('from')
        print(header[0])
        print(header[1])

    def add_to_buffer(self, shit):
        self.peer.add_command(shit)


class InputReader(threading.Thread):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setDaemon(True)

    def run(self):
        while True:
            s = input()
            self.ui.add_to_buffer(s)


Builder.load_string("""
<Root_or_Client>:
    BoxLayout:
        Button:
            text: 'Root'
            on_press:
                root.manager.set_is_root(True)
                root.manager.transition.direction = 'left'
                root.manager.current = 'home'
                root.manager.start_peer()
                root.manager.set()
        Button:
            text: 'Client'  
            on_press:
                root.manager.set_is_root(False)
                root.manager.transition.direction = 'left'
                root.manager.current = 'root_address'          

<User_Address>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: 'IP:' 
            TextInput:
                id: userIP
        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: 'Port:' 
            TextInput:
                id: userPort
        Button:
            text: 'Next'
            on_press:
                root.manager.transition.direction = 'left'
                root.manager.current = 'root_or_client'
                root.set_address()
<Root_Address>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: 'Root IP:' 
            TextInput:
                id: rootIP
        BoxLayout:
            orientation: 'horizontal'
            Label:
                text: 'Root Port:' 
            TextInput:
                id: rootPort
        Button:
            text: 'Next'
            on_press:
                root.manager.transition.direction = 'left'
                root.manager.current = 'home'
                root.set_root_address()
                root.manager.start_peer()
                root.manager.set()
<HomePage>
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                orientation: 'vertical'
                BoxLayout:
                    orientation: 'horizontal'
                    Label:
                        id: connection
                        text: 'Disconnected'
                    Label:
                        id: ipLabel
                        text : 'IP:' + root.ip
                    Label:
                        id: portLabel
                        text: 'Port:' + root.port
                    Label:
                        id: is_root
                        text: root.root_client                           
                
                BoxLayout:
                    orientation: 'horizontal'
                    Label:
                        id: parent_ip_label
                        text: 'Parent IP:' + root.parent_ip
                    Label:
                        id: parent_port_label
                        text: 'Parent Port:' + root.parent_port
                    Label:
                        id:timer
                        text: root.timer
                        background_color: 1,0,0,0
            BoxLayout:
                ScrollView:
                    Label:
                        id: message
                        size_hint: None, None
                        size: self.texture_size
                        text: ''
        BoxLayout:
            orientation: 'horizontal'
            BoxLayout:
                orientation: 'vertical'
                Button:
                    text: 'Send Register'
                    on_press: root.send_register()
                Button:
                    text: 'Advertise'
                    on_press: root.send_advertise()
                TextInput:
                    id: message_input
                Button:
                    text: 'Send Message'
                    on_press: root.send_message()
            BoxLayout:
                ScrollView:
                    id: scroll
                    Label:
                        id: packet_display
                        size_hint: None, None
                        size: self.texture_size
                        text: ''
""")


class HomePage(Screen):
    def __init__(self, **kw):
        self.timer = '0'
        self.ip = ''
        self.port = '0'
        self.root_client = 'Client'
        self.parent_ip = ''
        self.parent_port = ''
        self.peer = None
        super().__init__(**kw)

    def display_message(self, message):
        self.ids.message.text += message + '\n\n'
        # nl = Label()
        # nl.text = message
        # self.ids.scroll.add_widget(nl)
    def display_pkt(self, pkt):
        self.ids.packet_display.text += 'Header: ' + pkt.get_header() + '\nBody: ' + pkt.get_body() + '\n\n'

    def update_stats(self):
        self.update_screen()

    def update_screen(self):
        if self.peer.parent is None:
            self.ids.parent_ip_label.text = 'Parent IP: '
            self.ids.parent_port_label.text = 'Port IP:'
        else:
            self.ids.parent_ip_label.text = 'Parent IP: ' + str(self.peer.parent[0])
            self.ids.parent_port_label.text = 'Port IP:' + str(self.peer.parent[1])
        self.ids.timer.text = str(self.peer.since_last)
        if self.peer.is_connected:
            self.ids.connection.text = 'Connected'
        else:
            self.ids.connection.text = 'Disconnected'

    def send_register(self):
        self.peer.add_command('register')

    def send_advertise(self):
        self.peer.add_command('advertise')

    def send_message(self):
        message = 'send_message ' + self.ids.message_input.text
        self.ids.message_input.text = ''
        self.peer.add_command(message)

    def first_build(self):
        self.ids.ipLabel.text = self.ip
        self.ids.portLabel.text = self.port
        self.ids.is_root.text = self.root_client


class Root_or_Client(Screen):
    def print(self):
        print('sfgdg')

    pass


class User_Address(Screen):
    def __init__(self, sm, **kw):
        super().__init__(**kw)
        self.sm = sm

    def set_address(self):
        ip = self.ids.userIP.text
        port = self.ids.userPort.text
        self.sm.set_address(ip, port)

    pass


class Root_Address(Screen):
    def __init__(self, sm, **kw):
        super().__init__(**kw)
        self.sm = sm

    def set_root_address(self):
        ip = self.ids.rootIP.text
        port = self.ids.rootPort.text
        self.sm.set_root_address(ip, port)




class Screen_manager(ScreenManager):
    def __init__(self, home, **kwargs):
        super().__init__(**kwargs)
        self.peer = None
        self.is_root = False
        self.address = None
        self.root_address = None
        self.home = home

    def print(self, s):
        print(s)

    def set_is_root(self, input):
        self.is_root = input

    def set_address(self, ip, port):
        self.address = Node.parse_address((ip, port))
        print(self.address)

    def set_root_address(self, ip, port):
        self.root_address = Node.parse_address((ip, port))
        print(self.root_address)

    def start_peer(self):
        self.peer = Peer(self.address[0], self.address[1], self.is_root, self, self.root_address)
        self.peer.setDaemon(True)
        self.peer.start()

    def set(self):
        self.home.timer = '0'
        self.home.ip = self.address[0]
        self.home.port = self.address[1]
        if self.is_root:
            self.home.root_client = 'Root'
        else:
            self.home.root_client = 'Client'

        self.home.first_build()
        self.home.peer = self.peer
        self.home.update_stats()

    def display_message(self, message):
        self.home.display_message(message)

    def display_pkt(self, pkt):
        self.home.display_pkt(pkt)
        print('header: ')
        print(pkt.get_header())
        print('body: ')
        print(str(pkt.get_body()))

    def update_stats(self):
        self.home.update_stats()


class GIU(App):
    def print(self):
        print('sfgdg')

    def build(self):
        hp = HomePage(name='home')
        sm = Screen_manager(hp)
        self.hp = hp
        sm.add_widget(User_Address(name='user_address', sm=sm))
        sm.add_widget(Root_or_Client(name='root_or_client'))
        sm.add_widget(Root_Address(name='root_address', sm=sm))
        sm.add_widget(hp)
        return sm

    def on_stop(self):
        self.hp.peer.stop = True
        self.hp.peer.timer.stop = True
        sys.exit()


if __name__ == '__main__':
    ui = GIU()
    ui.run()

# if __name__ == '__main__':
#     ui = UI()
