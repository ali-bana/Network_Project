from src.Stream import Stream

def callback(address, data):
    print(address[0])
    print(address[1])
    print(data)


print('sdfgg')
address = (('localhost', 8888))
print('sdfgg1')
s = Stream('localhost', 6666, callback)
print('sdfdfkklkl')
s.add_node(address)
s.add_message_to_out_buff(address, bytes('aliali', 'UTF-8'))
s.send_out_buf_messages(False)



from src.Packet import PacketFactory
from src.Packet import Packet

#
# def printPacket(p):
#     print(p.version)
#     print(p.type)
#     print(p.length)
#     print(p.sender_ip)
#     print(p.sender_port)
#     print(p.body)

#
# pk = PacketFactory.new_message_packet('this',('092.168.1.1', 66))
# pk = PacketFactory.new_advertise_packet('REQ', ('092.168.1.1', 66))
# pk = PacketFactory.new_advertise_packet('RES', ('092.168.1.1', 66), ('092.168.1.1', 66))
# pk = PacketFactory.new_join_packet(('092.168.1.1', 66))
# pk = PacketFactory.new_register_packet('REQ', ('092.168.1.1', 66))
# pk = PacketFactory.new_register_packet('RES', ('092.168.1.1', 66))
# nodes = [('168.1.1.1', 456), ('108.143.1.1', 456), ('21.88.1.0', 456), ('168.43.1.3', 456)]
# pk = PacketFactory.new_reunion_packet('REQ', ('092.168.1.1', 66), nodes)
# pk = PacketFactory.new_reunion_packet('RES', ('092.168.1.1', 66), nodes)
# print(pk)
# print('\n\n')
# printPacket(PacketFactory.parse_buffer(pk))
