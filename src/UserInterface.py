import threading
from src.Peer import Peer
# from kivy.app import App
# from kivy.lang import Builder
# from kivy.uix.screenmanager import ScreenManager, Screen
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


# Builder.load_string("""
# <Root_or_Client>:
#     BoxLayout:
#         Button:
#             text: 'Goto settings'
#             on_press:
#                 root.manager.transition.direction = 'left'
#                 root.manager.current = 'settings'
#         Button:
#             text: 'Quit'
#             root.mf()
#
# <SettingsScreen>:
#     BoxLayout:
#         Button:
#             text: 'My settings button'
#         Button:
#             text: 'Back to menu'
#             on_press:
#                 root.manager.transition.direction = 'right'
#                 root.manager.current = 'menu'
# """)
#
# # Declare both screens
# class Root_or_Client(Screen):
#     pass
#
# class SettingsScreen(Screen):
#     pass
#
# # Create the screen manager
# sm = ScreenManager()
# sm.add_widget(Root_or_Client(name='menu'))
# sm.add_widget(SettingsScreen(name='settings'))
#
# class TestApp(App):
#
#
#     def build(self):
#         return sm



if __name__ == '__main__':
    ui = UI()
