from src.Stream import Stream
from src.Packet import Packet, PacketFactory
from src.tools.SemiNode import SemiNode
from src.tools.NetworkGraph import NetworkGraph, GraphNode
import time
import threading
import queue
from src.tools.Node import Node
from src.tools.NetworkGraph import NetworkGraph
from src.tools.NetworkGraph import GraphNode

"""
    Peer is our main object in this project.
    In this network Peers will connect together to make a tree graph.
    This network is not completely decentralised but will show you some real-world challenges in Peer to Peer networks.
    
"""


class Peer(threading.Thread):
    def __init__(self, server_ip, server_port, is_root, ui, root_address=None):
        """
        The Peer object constructor.

        Code design suggestions:
            1. Initialise a Stream object for our Peer.
            2. Initialise a PacketFactory object.
            3. Initialise our UserInterface for interaction with user commandline.
            4. Initialise a Thread for handling reunion daemon.

        Warnings:
            1. For root Peer, we need a NetworkGraph object.
            2. In root Peer, start reunion daemon as soon as possible.
            3. In client Peer, we need to connect to the root of the network, Don't forget to set this connection
               as a register_connection.


        :param server_ip: Server IP address for this Peer that should be pass to Stream.
        :param server_port: Server Port address for this Peer that should be pass to Stream.
        :param is_root: Specify that is this Peer root or not.
        :param root_address: Root IP/Port address if we are a client.

        :type server_ip: str
        :type server_port: int
        :type is_root: bool
        :type root_address: tuple
        """
        super().__init__()
        self.ui_buffer = queue.Queue()
        self.stream = Stream(server_ip, server_port)
        self.ip = Node.parse_ip(server_ip)
        self.port = Node.parse_port(str(server_port))

        self.address = (self.ip, int(self.port))
        self.setDaemon(True)
        self.ui = ui
        self.is_root = is_root
        self.root_address = self.address
        if not is_root:
            self.root_address = root_address
        self.children = []
        self.is_reunion_running = False
        self.parent = None
        self.is_connected = False
        # self.reunion_timer = ReunionTimer(self)
        self.graph = NetworkGraph(GraphNode(self.root_address))
        if not self.is_root:
            print('making the shit')
            self.stream.add_node(self.root_address, True)

        self.r_h_b_received = True
        self.since_last = 0
        self.timer = Timer(self)
        self.timer.start()

    def start_user_interface(self):
        """
        For starting UserInterface thread.

        :return:
        """
        # in our code userinterface starts this shit
        pass

    def add_command(self, command):
        self.ui_buffer.put(command)

    def handle_user_interface_buffer(self):
        """
        In every interval, we should parse user command that buffered from our UserInterface.
        All of the valid commands are listed below:
            1. Register:  With this command, the client send a Register Request packet to the root of the network.
            2. Advertise: Send an Advertise Request to the root of the network for finding first hope.
            3. SendMessage: The following string will be added to a new Message packet and broadcast through the network.

        Warnings:
            1. Ignore irregular commands from the user.
            2. Don't forget to clear our UserInterface buffer.
        :return:
        """
        while not self.ui_buffer.empty():

            command = self.ui_buffer.get()
            command = str(command)
            s = (command.split(' '))
            if s[0] == 'send_message':
                print('send message')
                self.send_message(command[13:])
                pass
            elif s[0] == 'join':
                print('join')
                self.send_join()
                pass
            elif s[0] == 'register':
                print('send register')
                self.send_register()
                pass
            elif s[0] == 'advertise':
                print('advertise')
                self.send_advertise()
            elif s[0] == 'regi':
                print('registered:')
                for reged in self.graph.registered:
                    print(reged.get_address()[0])
                    print(reged.get_address()[1])
            elif s[0] == 're':
                self.send_reunion()
                pass
            elif s[0] == 'par':
                print(self.parent)
            elif s[0] == 'ch':
                for address in self.children:
                    print(address)

        pass

    def send_advertise(self):
        if not self.is_root:
            pkt = PacketFactory.new_advertise_packet('REQ', self.address)
            self.stream.add_message_to_out_buff(self.root_address, pkt)
        pass

    def send_register(self):
        if not self.is_root:
            pkt = PacketFactory.new_register_packet('REQ', self.address, self.address)
            # self.ui.display_pkt(PacketFactory.parse_buffer(pkt))
            self.stream.add_message_to_out_buff(self.root_address, pkt)
        pass

    def send_message(self, s):
        print('sending mesaage to:')
        pkt = PacketFactory.new_message_packet(s, self.address)
        for address in self.children:
            print(address)
            self.stream.add_message_to_out_buff(address, pkt)
        if not (self.is_root) and (self.address is not None):
            print(self.parent)
            self.stream.add_message_to_out_buff(self.parent, pkt)
        pass

    def send_join(self):
        pkt = PacketFactory.new_join_packet(self.address)
        self.stream.add_message_to_out_buff(self.parent, pkt)
        self.is_connected = True
        pass

    def run(self):
        """
        The main loop of the program.

        Code design suggestions:
            1. Parse server in_buf of the stream.
            2. Handle all packets were received from our Stream server.
            3. Parse user_interface_buffer to make message packets.
            4. Send packets stored in nodes buffer of our Stream object.
            5. ** sleep the current thread for 2 seconds **

        Warnings:
            1. At first check reunion daemon condition; Maybe we have a problem in this time
               and so we should hold any actions until Reunion acceptance.
            2. In every situation checkout Advertise Response packets; even is Reunion in failure mode or not

        :return:
        """
        while True:
            # if not self.is_connected:
            #     self.stream.clear_in_buff()
            #     self.stream.clear_out_buff()
            #     self.stream.clear_not_reg_nodes()

            # print('we R in loop')
            self.read_stream_in_buffer()
            self.handle_user_interface_buffer()
            self.stream.send_out_buf_messages()
            time.sleep(2)

    def read_stream_in_buffer(self):
        buffers = self.stream.read_in_buf()
        for buffer in buffers:
            print(buffer)
            packet = PacketFactory.parse_buffer(buffer)
            if packet is None:
                continue
            if packet.length + 20 != len(buffer):
                continue
            self.handle_packet(packet)

        self.stream.clear_in_buff()

    def run_reunion_daemon(self):

        """

        In this function, we will handle all Reunion actions.

        Code design suggestions:
            1. Check if we are the network root or not; The actions are identical.
            2. If it's the root Peer, in every interval check the latest Reunion packet arrival time from every node;
               If time is over for the node turn it off (Maybe you need to remove it from our NetworkGraph).
            3. If it's a non-root peer split the actions by considering whether we are waiting for Reunion Hello Back
               Packet or it's the time to send new Reunion Hello packet.

        Warnings:
            1. If we are the root of the network in the situation that we want to turn a node off, make sure that you will not
               advertise the nodes sub-tree in our GraphNode.
            2. If we are a non-root Peer, save the time when you have sent your last Reunion Hello packet; You need this
               time for checking whether the Reunion was failed or not.
            3. For choosing time intervals you should wait until Reunion Hello or Reunion Hello Back arrival,
               pay attention that our NetworkGraph depth will not be bigger than 8. (Do not forget main loop sleep time)
            4. Suppose that you are a non-root Peer and Reunion was failed, In this time you should make a new Advertise
               Request packet and send it through your register_connection to the root; Don't forget to send this packet
               here, because in the Reunion Failure mode our main loop will not work properly and everything will be got stock!

        :return:
        """
        # self.reunion_timer.start()
        pass

    def send_broadcast_packet(self, broadcast_packet):
        """

        For setting broadcast packets buffer into Nodes out_buff.

        Warnings:
            1. Don't send Message packets through register_connections.

        :param broadcast_packet: The packet that should be broadcast through the network.
        :type broadcast_packet: Packet

        :return:
        """
        nodes = self.stream.get_not_register_nodes()
        for node in nodes:
            self.stream.add_message_to_out_buff(node.get_server_address(), broadcast_packet)
        pass

    def handle_packet(self, packet):
        """

        This function act as a wrapper for other handle_###_packet methods to handle the packet.

        Code design suggestion:
            1. It's better to check packet validation right now; For example Validation of the packet length.

        :param packet: The arrived packet that should be handled.

        :type packet Packet

        """
        print('this is handle packet')
        self.ui.display_pkt(packet)
        if packet.type == 1:
            self.__handle_register_packet(packet)
            return
        elif packet.type == 2:
            self.__handle_advertise_packet(packet)
            pass
        elif packet.type == 3:
            self.__handle_join_packet(packet)
            pass
        elif packet.type == 4:
            self.__handle_message_packet(packet)
            pass
        elif packet.type == 5:
            self.__handle_reunion_packet(packet)
            pass
        pass

    def __check_registered(self, source_address):
        """
        If the Peer is the root of the network we need to find that is a node registered or not.

        :param source_address: Unknown IP/Port address.
        :type source_address: tuple

        :return:
        """
        return self.graph.is_registered(source_address)
        pass

    def __handle_advertise_packet(self, packet):
        """
        For advertising peers in the network, It is peer discovery message.

        Request:
            We should act as the root of the network and reply with a neighbour address in a new Advertise Response packet.

        Response:
            When an Advertise Response packet type arrived we should update our parent peer and send a Join packet to the
            new parent.

        Code design suggestion:
            1. Start the Reunion daemon thread when the first Advertise Response packet received.
            2. When an Advertise Response message arrived, make a new Join packet immediately for the advertised address.

        Warnings:
            1. Don't forget to ignore Advertise Request packets when you are a non-root peer.
            2. The addresses which still haven't registered to the network can not request any peer discovery message.
            3. Maybe it's not the first time that the source of the packet sends Advertise Request message. This will happen
               in rare situations like Reunion Failure. Pay attention, don't advertise the address to the packet sender
               sub-tree.
            4. When an Advertise Response packet arrived update our Peer parent for sending Reunion Packets.

        :param packet: Arrived register packet

        :type packet Packet

        :return:
        """
        if (packet.body[0:3] == 'RES') and (not self.is_root):
            self.children.clear()
            self.stream.remove_not_reg_nodes()
            self.parent = Node.parse_address((packet.body[3:18], packet.body[18:23]))
            self.stream.add_node(self.parent)
            join = PacketFactory.new_join_packet(self.address)
            self.stream.add_message_to_out_buff(self.parent, join)
            self.is_connected = True
            # now we are connected
        elif (packet.body[0:3] == 'REQ') and (self.is_root):
            if not self.graph.is_registered(packet.get_source_server_address()):
                return
            address = self.graph.find_live_node(packet.get_source_server_address()).get_address()
            if address is None:
                return
            self.graph.add_node(packet.sender_ip, packet.sender_port, address)
            res_pkt = PacketFactory.new_advertise_packet('RES', self.address, address)
            self.stream.add_message_to_out_buff(packet.get_source_server_address(), res_pkt)
        pass

    def __handle_register_packet(self, packet):
        """
        For registration a new node to the network at first we should make a Node with stream.add_node for'sender' and
        save it.

        Code design suggestion:
            1.For checking whether an address is registered since now or not you can use SemiNode object except Node.

        Warnings:
            1. Don't forget to ignore Register Request packets when you are a non-root peer.

        :param packet: Arrived register packet
        :type packet Packet
        :return:
        """
        source_address = (packet.sender_ip, packet.sender_port)
        if self.is_root and (not self.__check_registered(source_address)):
            self.graph.register(source_address)
            self.stream.add_node(source_address, True)
            res_pkt = PacketFactory.new_register_packet('RES', self.address)
            self.stream.add_message_to_out_buff(source_address, res_pkt)
        pass

    def __check_neighbour(self, address):
        """
        It checks is the address in our neighbours array or not.

        :param address: Unknown address

        :type address: tuple

        :return: Whether is address in our neighbours or not.
        :rtype: bool
        """
        if (address[0] == self.parent[0]) & (address[1] == self.parent[1]):
            return True
        for add in self.children:
            if (address[0] == add[0]) & (address[1] == add[1]):
                return True
        return False
        pass

    def __handle_message_packet(self, packet):
        """
        Only broadcast message to the other nodes.

        Warnings:
            1. Do not forget to ignore messages from unknown sources.
            2. Make sure that you are not sending a message to a register_connection.

        :param packet: Arrived message packet

        :type packet Packet

        :return:
        """
        if not self.child_or_parent(packet.get_source_server_address()):
            return
        message = packet.get_body()
        self.ui.display_message('this is message' + message)
        res_pkt = PacketFactory.new_message_packet(message, self.address)
        print('trying to send packet to:')
        for address in self.children:
            if not self.address_equal(address, packet.get_source_server_address()):
                self.stream.add_message_to_out_buff(address, res_pkt)
                print(address)
        if (not self.is_root) and (self.parent is not Node):
            if self.address_equal(self.parent, packet.get_source_server_address()):
                return
            print(self.parent)
            self.stream.add_message_to_out_buff(self.parent, res_pkt)

    def address_equal(self, address1, address2):
        address1 = Node.parse_address(address1)
        address2 = Node.parse_address(address2)
        return (address1[0] == address2[0]) and (address1[1] == address2[1])

    def child_or_parent(self, input):
        for address in self.children:
            if self.address_equal(input, address):
                return True
        if self.parent is not Node:
            if self.address_equal(input, self.parent):
                return True
        return False
        pass

    def __handle_reunion_packet(self, packet):
        """
        In this function we should handle Reunion packet was just arrived.

        Reunion Hello:
            If you are root Peer you should answer with a new Reunion Hello Back packet.
            At first extract all addresses in the packet body and append them in descending order to the new packet.
            You should send the new packet to the first address in the arrived packet.
            If you are a non-root Peer append your IP/Port address to the end of the packet and send it to your parent.

        Reunion Hello Back:
            Check that you are the end node or not; If not only remove your IP/Port address and send the packet to the next
            address, otherwise you received your response from the root and everything is fine.

        Warnings:
            1. Every time adding or removing an address from packet don't forget to update Entity Number field.
            2. If you are the root, update last Reunion Hello arrival packet from the sender node and turn it on.
            3. If you are the end node, update your Reunion mode from pending to acceptance.


        :param packet: Arrived reunion packet
        :return:
        """
        nodes = PacketFactory.parse_reunion_packet_body(packet.body)

        if self.is_root:
            if packet.body[0:3] == 'RES':
                return
            self.graph.reunion_arrived(nodes[0])
            nodes.reverse()
            res_pkt = PacketFactory.new_reunion_packet('RES', self.address, nodes)
            self.stream.add_message_to_out_buff(packet.get_source_server_address(), res_pkt)
            print('hello back sent to')
            print(packet.get_source_server_address())
            return
        else:
            if packet.body[0:3] == 'REQ':
                nodes.append(self.address)
                res_pkt = PacketFactory.new_reunion_packet('REQ', self.address, nodes)
                self.stream.add_message_to_out_buff(self.parent, res_pkt)
                return
            else:
                nodes = PacketFactory.parse_reunion_packet_body(packet.body)
                if not self.address_equal(nodes[0], self.address):
                    return
                if len(nodes) == 1:
                    # print('bla bla bla bla bla bla')
                    self.reunion_back_arrived()
                    return
                # print('kiiiiir')
                nodes.remove(nodes[0])
                res_pkt = PacketFactory.new_reunion_packet('RES', self.address, nodes)
                self.stream.add_message_to_out_buff(nodes[0], res_pkt)
                return

        pass

    def __handle_join_packet(self, packet):
        """
        When a Join packet received we should add a new node to our nodes array.
        In reality, there is a security level that forbids joining every node to our network.

        :param packet: Arrived register packet.


        :type packet Packet

        :return:
        """
        self.children.append((packet.sender_ip, packet.sender_port))
        self.stream.add_node((packet.sender_ip, packet.sender_port))
        pass

    def __get_neighbour(self, sender):
        """
        Finds the best neighbour for the 'sender' from the network_nodes array.
        This function only will call when you are a root peer.

        Code design suggestion:
            1. Use your NetworkGraph find_live_node to find the best neighbour.

        :param sender: Sender of the packet
        :return: The specified neighbour for the sender; The format is like ('192.168.001.001', '05335').
        """
        pass

    # def reunion_failed_notify(self):
    #     self.reunion_timer.stop()
    #     self.is_connected = False
    #     pass

    def send_reunion(self):
        if not self.is_connected:
            return
        pkt = PacketFactory.new_reunion_packet('REQ', self.address, [self.address])
        self.stream.add_message_to_out_buff(self.parent, pkt)
        self.since_last = 0
        self.r_h_b_received = False

    def disconnect(self):
        self.is_connected = False
        self.parent = None
        self.stream.remove_not_reg_nodes()
        self.stream.clear_in_buff()
        # maybe we need some more shit

    def sec_passed(self):
        # print('........')
        # print(self.is_root)
        # print(self.is_connected)
        # print(self.r_h_b_received)
        # print(self.since_last)
        # print('........')
        if self.is_connected and (not self.is_root):
            self.since_last += 1
            if (not self.r_h_b_received) and (self.since_last > 50):
                self.disconnect()
                return
            elif (self.r_h_b_received) and (self.since_last > 4):
                self.send_reunion()
        if self.is_root:
            self.graph.increment_time()
        pass

    def reunion_back_arrived(self):
        self.r_h_b_received = True


class Timer(threading.Thread):
    def __init__(self, peer):
        super().__init__()
        self.peer = peer
        self.daemon = True

    def run(self):
        while True:
            time.sleep(1)
            self.peer.sec_passed()

# class ReunionTimer(threading.Thread):
#     def __init__(self, peer):
#         super().__init__()
#         self.peer = peer
#         self.timer = 0
#         self.received = False
#         self.setDaemon(True)
#         self.last_sent = 0
#         self.has_on_fly = False
#         self.stoper = False
#
#     def sent_reunion(self):
#         self.timer = 0
#         self.has_on_fly = True
#         self.run()
#         self.received = False
#         self.last_sent = 0
#
#     def run(self):
#
#         while not self.stoper:
#             time.sleep(1)
#             if self.has_on_fly:
#                 self.timer += 1
#                 if self.timer > 16:
#                     self.peer.reunion_failed_notify()
#                     return
#             self.last_sent += 1
#             if self.should_send_reunion():
#                 self.peer.send_reunion()
#
#     def receive(self):
#         self.received = True
#         self.has_on_fly = False
#         self.timer = 0
#
#     def should_send_reunion(self):
#         return (not self.has_on_fly) and (self.last_sent > 4)
#
#     def stop(self):
#         self.stoper = True
