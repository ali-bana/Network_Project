from src.Stream import Stream

# def callback(address, data):
#     print(address[0])
#     print(address[1])
#     print(data)
#
#
# print('sdfgg')
# address = (('localhost', 8888))
# print('sdfgg1')
# s = Stream('localhost', 6666, callback)
# print('sdfdfkklkl')
# s.add_node(address)
# s.add_message_to_out_buff(address, bytes('aliali', 'UTF-8'))
# s.send_out_buf_messages(False)
#

from src.Packet import PacketFactory
pk = PacketFactory.new_message_packet('this is the end hold your breath and count to 10',('192.168.1.1', 666))
print(PacketFactory.parse_buffer(pk))



