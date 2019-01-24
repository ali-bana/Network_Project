import time
import queue
from src.tools.Node import Node


class GraphNode:
    def __init__(self, address):
        """

        :param address: (ip, port)
        :type address: tuple

        """
        self.is_on = False
        self.parent = None
        self.address = address
        self.children = []
        self.sinceLastReunion = 0
        pass

    def set_parent(self, parent):
        self.parent = parent
        pass

    def set_address(self, new_address):
        self.address = new_address
        pass

    def reset(self):
        self.is_on = False
        self.children.clear()
        self.parent = None
        self.sinceLastReunion = 0
        pass

    def add_child(self, child):
        self.children.append(child)
        pass

    def get_address(self):
        return Node.parse_address(self.address)

    def get_is_on(self):
        return self.is_on

    def turn_on(self):
        if not self.is_on:
            self.is_on = True
            self.sinceLastReunion = 0

    def inc_time(self):
        self.sinceLastReunion += 1
        return self.sinceLastReunion

    def reset_timer(self):
        self.sinceLastReunion = 0

class NetworkGraph:
    def __init__(self, root):
        self.root = root
        self.root.is_on = True
        self.nodes = [root]
        self.registered = []


    def increment_time(self):
        for node in self.nodes:
            if (node.inc_time() > 40) and (node is not self.root):
                self.turn_off_node(node.get_address())

    def reunion_arrived(self, sender):
        node = self.find_node(sender[0], sender[1])
        if node is not None:
            node.reset_timer()

    def find_live_node(self, sender):
        """
        Here we should find a neighbour for the sender.
        Best neighbour is the node who is nearest the root and has not more than one child.

        Code design suggestion:
            1. Do a BFS algorithm to find the target.

        Warnings:
            1. Check whether there is sender node in our NetworkGraph or not; if exist do not return sender node or
               any other nodes in it's sub-tree.

        :param sender: The node address we want to find best neighbour for it.
        :type sender: tuple

        :return: Best neighbour for sender.
        :rtype: GraphNode
        """

        node = self.find_node(sender[0], sender[1])
        if node is None:
            return
        if node.get_is_on():
            self.turn_off_node(sender)
        q = queue.Queue()
        q.put(self.root)
        # print('fnbkngkbn')
        while not q.empty():
            n = q.get()
            # print(n)
            if len(n.children) < 2:
                return n
            for a in n.children:
                q.put(a)
        pass

    def register_node(self, address):
        self.registered.append(GraphNode(address))

    def find_node(self, ip, port):
        input = Node.parse_address((ip, port))
        for g_node in self.nodes:
            if (g_node.get_address()[0] == input[0]) and (g_node.get_address()[1] == input[1]):
                return g_node
        for g_node in self.registered:
            if (g_node.get_address()[0] == input[0]) and (g_node.get_address()[1] == input[1]):
                return g_node

        pass

    def turn_on_node(self, node_address):

        pass

    def turn_off_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        if node.get_is_on():
            q = queue.Queue()
            q.put(node)
            node.parent.children.remove(node)
            while not q.empty():
                n = q.get()
                for a in n.children:
                    q.put(a)
                n.is_on = False
                self.nodes.remove(n)
                self.registered.append(n)
                n.reset()

        pass

    def remove_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        self.turn_off_node(node_address)
        self.registered.remove(node)
        pass

    def register(self, address):
        node = self.find_node(address[0], address[1])
        if node is None:
            self.register_node(address)

    def add_node(self, ip, port, father_address):
        """
        Add a new node with node_address if it does not exist in our NetworkGraph and set its father.

        Warnings:
            1. Don't forget to set the new node as one of the father_address children.
            2. Before using this function make sure that there is a node which has father_address.

        :param ip: IP address of the new node.
        :param port: Port of the new node.
        :param father_address: Father address of the new node

        :type ip: str
        :type port: int
        :type father_address: tuple


        :return:
        """
        node = self.find_node(ip, port)
        father = self.find_node(father_address[0], father_address[1])
        if (node is not None) and (father is not None):
            self.nodes.append(node)
            node.set_parent(father)
            father.add_child(node)
            node.turn_on()
            try:
                self.registered.remove(node)
            except:
                pass
            return True
        return False

    def is_registered(self, address):
        return self.find_node(address[0], address[1]) is not None
