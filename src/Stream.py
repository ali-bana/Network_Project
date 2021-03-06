from src.tools.simpletcp.tcpserver import ServerSocket
from src.tools.simpletcp.tcpserver import TCPServer
from src.tools.Node import Node
import threading


class Stream:

    def callback(self, address, queue, data):
        """
        The callback function will run when a new data received from server_buffer.

        :param address: Source address.
        :param queue: Response queue.
        :param data: The data received from the socket.
        :return:
        """
        queue.put(bytes('ACK', 'utf8'))
        self._server_in_buf.append(data)
        # self.app_call_back(address, data)

    pass

    def __init__(self, ip, port, ui):
        """
        The Stream object constructor.

        Code design suggestion:
            1. Make a separate Thread for your TCPServer and start immediately.


        :param ip: 15 characters
        :param port: 5 characters

        """
        self.ip = Node.parse_ip(ip)
        self.port = int(Node.parse_port(port))
        self.server = TCPServer(self.ip, self.port, self.callback, 1000, 2048)
        self.server.start()
        self._server_in_buf = []
        self.nodes = []
        self.out_buffer = []
        self.ui = ui

    def clear_out_buff(self):
        self.out_buffer.clear()

    def clear_not_reg_nodes(self):
        for node in self.nodes:
            if not node.is_register:
                self.nodes.remove(node)

    def get_server_address(self):
        """

        :return: Our TCPServer address
        :rtype: tuple
        """
        return self.ip, self.port
        pass

    def clear_in_buff(self):
        """
        Discard any data in TCPServer input buffer.

        :return:
        """
        self._server_in_buf.clear()

    def add_node(self, server_address, set_register_connection=False):
        """
        Will add new a node to our Stream.

        :param server_address: New node TCPServer address.
        :param set_register_connection: Shows that is this connection a register_connection or not.

        :type server_address: tuple
        :type set_register_connection: bool

        :return:
        """
        try:
            self.nodes.append(Node((Node.parse_ip(server_address[0]), int(Node.parse_port(server_address[1]))), False,
                               set_register_connection))
            return True
        except:
            self.ui.display_message('Could not Establish Connection!')
            return False
        pass

    def remove_node(self, node):
        """
        Remove the node from our Stream.

        Warnings:
            1. Close the node after deletion.

        :param node: The node we want to remove.
        :type node: Node

        :return:
        """
        try:
            self.nodes.remove(node)
        except:
            pass
        node.close()
        pass

    def get_node_by_server(self, ip, port):
        """

        Will find the node that has IP/Port address of input.

        Warnings:
            1. Before comparing the address parse it to a standard format with Node.parse_### functions.

        :param ip: input address IP
        :param port: input address Port

        :return: The node that input address.
        :rtype: Node
        """
        input = Node.parse_address((ip, port))
        # print('.........')
        # print(input[0])
        # print(input[1])
        # print('.........')
        # print(len(self.nodes))
        for node in self.nodes:
            add = Node.parse_address(node.get_server_address())
            # print('xxxxxxxxxxxx')
            # print(add[0])
            # print(add[1])
            # print('xxxxxxxxxxxx')
            if (input[0] == add[0]) and (input[1] == add[1]):
                return node

        pass

    def add_message_to_out_buff(self, address, message):
        """
        In this function, we will add the message to the output buffer of the node that has the input address.
        Later we should use send_out_buf_messages to send these buffers into their sockets.

        :param address: Node address that we want to send the message
        :param message: Message we want to send

        Warnings:
            1. Check whether the node address is in our nodes or not.

        :return:
        """

        node = self.get_node_by_server(address[0], address[1])

        if node is not None:
            self.out_buffer.append((message, node))
            return
        # print('this is out buffer')
        #         # for a in self.out_buffer:
        #         #     print(a[0])
        #         #     print(a[1])
        pass

    def read_in_buf(self):
        """
        Only returns the input buffer of our TCPServer.

        :return: TCPServer input buffer.
        :rtype: list
        """
        return self._server_in_buf

    def send_messages_to_node(self, node):
        """
        Send buffered messages to the 'node'

        Warnings:
            1. Insert an exception handler here; Maybe the node socket you want to send the message has turned off and
            you need to remove this node from stream nodes.

        :param node:
        :type node Node

        :return:
        """
        for a in self.out_buffer:
            if a[1] == node:
                node.add_message_to_out_buff(a[0])
                self.out_buffer.remove(a)
            node.send_message()

        pass

    def send_out_buf_messages(self, only_register=False):
        """
        In this function, we will send hole out buffers to their own clients.

        :return:
        """
        # dont know only register fucking meaning
        # print('this is send_out_buf_messages')
        # print(len(self.out_buffer))
        for a in self.out_buffer:
            # print(a[0])
            try:
                a[1].add_message_to_out_buff(a[0])
                a[1].send_message()
            except:
                print('this bastard is not listening')
                self.remove_node(a[1])
        self.out_buffer = []

    def get_not_register_nodes(self):
        result = []
        for node in self.nodes:
            if not node.is_register:
                result.append(node)
        return result

    def remove_not_reg_nodes(self):
        for node in self.nodes:
            if not node.is_register:
                node.close()
                self.nodes.remove(node)