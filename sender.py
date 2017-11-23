#!/usr/bin/python3

"""
Client code.

Packet layout
|IP header (20bytes)|UDP header (8bytes)|Payload|

Payload layout
|f_nack(4bits)|f_fin(1bit)|f_ack(1bit)|f_endTransaction(1bit)|f_newTransaction(1bit)|transactionId(4bytes)|segId(4bytes)|data|

Assuming server buffer is fixed at 65535 bytes. 
Max data size = 65535 - 20 - 8 - 1 - 4 - 4 = 65498

1.0Mbps = 125kBps
Sending packets of size BB Bytes, we have to send a packet every (BB Bytes)/(1.0*125000Bps) seconds
Or, time interval between packets = (BB Bytes)/(rate*125000Bps)

Use -r to select starting rate, default is 3.0Mbps
Use -a to select address to send data to, default is localhost
Use -p to select destination port number, default is 5555
Use -f to select file to send, default is a short message

On mininet, to send data to another host, please use -a <other host IP>, e.g. python ./client.py -a 10.0.0.2
"""

from socket import *
from struct import *
import argparse
import time
import sys

class Sender:
    message = 'hi how are you'.encode('UTF-8') # default message
    
    def __init__(self, rate, address, filename, portnum):
        self.updateFile(filename)
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.settimeout(0.01)
        self.receiver_address = (address, portnum)
        self.mtu = 6400
        self.packet_size = self.mtu
        self.data_payload_size = self.packet_size - 28 - 13
        self.timeinterval = self.packet_size/(rate*125000.0)
        
        self.total_message_length = len(self.message)
        self.tr_id = 353 # eventually unused
        self.max_window_size = 5
        self.window = [] # composite window. Only segIds that have not been ACKed will be in the window
        self.nextSegId = 0 # the next segment id to add into the window
        self.window_timer = []
        self.w_timeout = 0.2
        
        self.factor = 1
        self.safeConnect = 5
        self.dataLoss = 0
    
    def reset(self):
        self.mtu = 6400
        self.packet_size = self.mtu
        self.timeinterval = self.packet_size/(rate*125000.0)
        self.total_message_length = len(self.message)
        segId = 0
        self.tr_id = 353 # eventually unused
        self.max_window_size = 5
        self.window = [] # composite window. Only segIds that have not been ACKed will be in the window
        self.nextSegId = 0 # the next segment id to add into the window
        self.window_timer = []
        self.w_timeout = 0.2
        self.factor = 1
        self.safeConnect = 5
        self.dataLoss = 0
    
    def sendPacket(self, segId, d_size):
        # splice self.message to send
        msg = self.message[segId:segId+d_size]
        
        # calculate flags
        f_newTransaction = 1 if segId == 0 else 0
        f_endTransaction = 1 if segId+d_size >= self.total_message_length else 0
        f_ack = 0
        f_fin = 0 if self.window else 1
        flags = f_newTransaction + (f_endTransaction << 1) + (f_ack << 2) + (f_fin << 3)
        
        # encapsulate msg with our header
        msg_length = len(msg)
        payload = pack('!BIII' + str(msg_length) + 's', flags, self.tr_id, segId, len(self.message), msg) # struct pack is used to make sure that segId is always 4 bytes large, since integers in python are always 4 bytes
        
        # send packet
        sent = self.sock.sendto(payload, self.receiver_address)
    
    def addToWindow(self):
        while len(self.window) < self.max_window_size and self.nextSegId < len(self.message):
            if self.nextSegId + self.data_payload_size >= len(self.message):
                data_size = len(self.message)-self.nextSegId
            else:
                data_size = self.data_payload_size
            self.window.append((self.nextSegId, data_size))
            self.nextSegId += data_size
            self.window_timer.append(time.time() - self.w_timeout)
    
    def listenForAcks(self):
        if self.safeConnect > 5:
            self.safeConnect = 0
            self.factor += 1
            self.packet_size = min(self.mtu * self.factor, 65535)
            self.data_payload_size = self.packet_size - 28 - 13

        try:
            data, addr = self.sock.recvfrom(1024)
            
            self.safeConnect += 1
            flags, recSegId, recMsgLen = unpack('!BII', data)
            f_fin = flags & 2**3
            if recSegId < len(self.message):
                indexToChange = self.window.index((recSegId, recMsgLen))
                self.window.pop(indexToChange)
                self.window_timer.pop(indexToChange)
                self.addToWindow()
            if f_fin:
                return True
        except timeout:
            pass
        return False
    
    def updateFile(self, filename):
        if filename:
            with open(filename, 'rb') as input_file:
                self.message = input_file.read()
    
    def sendFile(self):
        starttime = time.time()
        nexttime = starttime - self.timeinterval # to make the client start sending data immediately instead of waiting for self.timeinterval
        self.addToWindow()
        
        while self.window:
            self.listenForAcks()
            if (time.time() - nexttime) < self.timeinterval: continue
            nexttime += self.timeinterval
            
            for i in range(len(self.window)):
                if time.time() - self.window_timer[i] > self.w_timeout:
                    self.dataLoss += 1
                    if self.dataLoss > 3:
                        self.safeConnect = 0
                        self.factor = 1 if self.factor <= 1 else self.factor-1
                        self.dataLoss = 0
                        self.packet_size = min(self.mtu * self.factor, 65535)
                        self.data_payload_size = self.packet_size - 28 - 13

                    segId, d_size = self.window[i]
                    self.sendPacket(segId, d_size)
                    self.window_timer[i] = time.time()

            sys.stdout.write("\rTime elapsed: %.3fs" % (time.time()-starttime))
            sys.stdout.flush()
        
        self.window_timer.append(time.time() - self.w_timeout)
        
        while True:
            if self.listenForAcks():
                break
            if (time.time() - nexttime) < self.timeinterval: continue
            nexttime += self.timeinterval
            
            if time.time() - self.window_timer[0] > self.w_timeout:
                self.sendPacket(len(self.message), 0)
                self.window_timer[0] = time.time()

            sys.stdout.write("\rTime elapsed: %.3fs" % (time.time()-starttime))
            sys.stdout.flush()
        print()
    
def main(rate, address, filename, portnum):
    s = Sender(rate, address, filename, portnum)
    s.sendFile()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-r', type=float, dest='rate', default=3.0, 
        help='Specify starting packet rate in Mbps (eg; -r 1.5 is 1.5 Mbps)')
    
    parser.add_argument('-a', type=str, dest='address', default='localhost', 
        help='Indicate the ip address to send the data to. Default is localhost. ')
    
    parser.add_argument('-f', type=str, dest='filename', default='', 
        help='Indicate the name of file to send')
    
    parser.add_argument('-p', type=int, dest='portnum', default=5555, 
        help='Indicate destination port. Default is 5555. ')
    
    args = parser.parse_args()
    
    print("Starting rate is %.1f Mbps\nSending to %s:%d" % (args.rate, args.address, args.portnum))
    main(args.rate, args.address, args.filename, args.portnum)



