from src.Stream import Stream
from src.Packet import PacketFactory
from src.tools.NetworkGraph import GraphNode
from src.tools.NetworkGraph import NetworkGraph
if __name__ == '__main__':
    # addressroot = ('localhost', 8888)
    # s = Stream('localhost', 6666)
    # s.add_node(addressroot)
    # s.add_message_to_out_buff(addressroot, PacketFactory.new_register_packet('REQ', addressroot, addressroot))
    # s.send_out_buf_messages()
    root = GraphNode(('localhost', 3333))
    n = NetworkGraph(root)

    print(n.find_node('localhost', 3333))

    n.register(('localhost', 4444))
    n.register(('localhost', 5555))
    n.register(('localhost', 6666))
    n.register(('localhost', 7777))
    n.register(('localhost', 8888))
    n.register(('localhost', 9999))
    n.register(('localhost', 1111))

    print(n.find_live_node(('localhost', 4444)))

    father = n.find_live_node(('localhost', 4444)).get_address()

    n.add_node('localhost', 4444, father)

    father = n.find_live_node(('localhost', 5555)).get_address()

    n.add_node('localhost', 5555, father)

    print('registered')

    for ng in n.registered:
        print(ng.get_address())

    father = n.find_live_node(('localhost', 6666)).get_address()

    n.add_node('localhost', 6666, father)

    father = n.find_live_node(('localhost', 7777)).get_address()

    n.add_node('localhost', 7777, father)

    father = n.find_live_node(('localhost', 8888)).get_address()

    n.add_node('localhost', 8888, father)



    n.turn_off_node(('localhost', 4444))

    for no in n.nodes:
        print(no.get_address())
        if no.parent is not None:
            print(no.parent.get_address())
        print('.......')