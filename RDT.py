from datetime import datetime, timedelta
import Network
import argparse
from time import sleep
import hashlib

class RDTException(Exception):
    pass

class Packet:
    # the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    # length of md5 checksum in hex
    checksum_length = 32
    
    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S
    
    @classmethod
    def from_byte_S(cls, byte_S):
        if Packet.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')
        # extract the fields
        seq_num = int(byte_S[Packet.length_S_length: Packet.length_S_length + Packet.seq_num_S_length])
        msg_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length + Packet.checksum_length:]
        return cls(seq_num, msg_S)
    
    def get_byte_S(self):
        # convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        # convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(
            self.length_S_length)
        # compute the checksum
        checksum = hashlib.md5((length_S + seq_num_S + self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        # compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S
    
    @staticmethod
    def corrupt(byte_S):
        # extract the fields
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length: Packet.length_S_length + Packet.seq_num_S_length]
        checksum_S = byte_S[
                     Packet.length_S_length + Packet.seq_num_S_length: Packet.length_S_length + Packet.seq_num_S_length + Packet.checksum_length]
        msg_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length + Packet.checksum_length:]
        
        # compute the checksum locally
        checksum = hashlib.md5(str(length_S + seq_num_S + msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()
        # and check if the same
        return checksum_S != computed_checksum_S


class RDT:
    # receive timeout
    timeout = timedelta(seconds=1)
    # latest sequence number used in a packet
    seq_num = 1
    # buffer of bytes read from network
    byte_buffer = ''
    
    def __init__(self, role_S, server_S, port):
        # use the passed in port and port+1 to set up unidirectional links between
        # RDT send and receive functions
        # cross the ports on the client and server to match net_snd to net_rcv
        if role_S == 'server':
            self.net_snd = Network.NetworkLayer(role_S, server_S, port)
            self.net_rcv = Network.NetworkLayer(role_S, server_S, port + 1)
        else:
            self.net_rcv = Network.NetworkLayer(role_S, server_S, port)
            self.net_snd = Network.NetworkLayer(role_S, server_S, port + 1)

    def disconnect(self):
        self.net_snd.disconnect()
        del self.net_snd
        self.net_rcv.disconnect()
        del self.net_rcv
    
    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        # !!! make sure to use net_snd link to udt_send and udt_receive in the RDT send function
        self.net_snd.udt_send(p.get_byte_S())
    
    def rdt_1_0_receive(self):
        start = datetime.now()
        while True:
            if datetime.now() - start > self.timeout:
                raise RDTException("timeout")
            # !!! make sure to use net_rcv link to udt_send and udt_receive the in RDT receive function
            byte_S = self.net_rcv.udt_receive()
            self.byte_buffer += byte_S
            # check if we have received enough bytes
            if len(self.byte_buffer) < Packet.length_S_length:
                # return ret_S  # not enough bytes to read packet length
                continue
            # extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                # return ret_S  # not enough bytes to read the whole packet
                continue
            # create packet from buffer content
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            # remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            # return packet message to the upper layer
            return p.msg_S
    
    def rdt_2_1_send(self, msg_S):
        pass
    
    def rdt_2_1_receive(self):
        pass
    
    def rdt_3_0_send(self, msg_S):
        pass
    
    def rdt_3_0_receive(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()
    
    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_1_0_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_1_0_receive())
        rdt.disconnect()
    else:
        sleep(1)
        print(rdt.rdt_1_0_receive())
        rdt.rdt_1_0_send('MSG_FROM_SERVER')
        rdt.disconnect()
