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

Use -r to select rate
Use -a to select address to send data to, default is localhost
Use -f to select file to send, default is a short message

On mininet, to send data to another host, please use -a <other host IP>, e.g. python ./client.py -a 10.0.0.2
"""

from socket import *
import argparse
from os import urandom
from struct import *
import time
import sys

def main(rate, address, filename):
    if filename:
        with open(filename, 'rb') as input_file:
            message = input_file.read()
    else:
        message = 'hi how are you'.encode('UTF-8')
    
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.settimeout(0.1)
    receiver_address = (address, 5555)
    
    def segsend(segId, data_payload_size):
        msg = message[segId:segId+data_payload_size] # spliced file contents
        msg_length = len(msg)
        f_newTransaction = 1 if segId == 0 else 0
        f_endTransaction = 1 if segId+data_payload_size >= len(message) else 0
        f_ack = 0
        f_fin = 0
        flags = f_newTransaction + (f_endTransaction << 1) + (f_ack << 2) + (f_fin << 3)
        #print(flags)
        #print('msg length %d' % msg_length)
        payload = pack('!BII' + str(msg_length) + 's', flags, tr_id, segId, msg) # struct pack is used to make sure that segId is always 4 bytes large, since integers in python are always 4 bytes
        sent = sock.sendto(payload, receiver_address)
    
    starttime = time.time()
    
    mtu = 64
    packet_size = mtu
    data_payload_size = packet_size - 28 - 9
    
    timeinterval = packet_size/(rate*125000.0)
    
    nexttime = starttime - timeinterval # to make the client start sending data immediately instead of waiting for timeinterval
    
    segId = 0
    tr_id = 353 # should be random
    window_size = 5
    
    window = [i*mtu for i in range(len(window_size))]
    window_i = [0] * window_size
    acked = []
    
    # the next segment id to add into the window
    nextSegId = mtu * window_size
    while window:
        try:
            data, addr = sock.recvfrom(1024)
            flags, recSegId, recMsgLen = unpack('!BII', data)
            f_fin = flags & 2**3
            
            
            indexToChange = window.indexOf(recSegId)
            window[indexToChange] = nextSegId
            window_i[indexToChange] = 0
            nextSegId += data_payload_size
            
            if f_fin:
                break
            #print("\nreceived message:", data,"\nflags:", flags, "\nrecSegId:", recSegId, "\nrecMsgLen:", recMsgLen)
        except:
            pass
        if (time.time() - nexttime) < timeinterval: continue
        nexttime += timeinterval
        
        for i in range(len(window_i)):
            if window_i[i] == 0:
                segsend(window[i], data_payload_size)

        #print('flags:',flags,'\npayload:',payload)
        #print('sent %d bytes' % (sent))
        sys.stdout.write("\rTime elapsed: %.3fs" % (time.time()-starttime))
        sys.stdout.flush()
        

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=float, dest='rate', default=3.0, 
        help='Packet rate in Mbps (eg; -r 1.5 is 1.5 Mbps)')
    
    parser.add_argument('-a', type=str, dest='address', default='localhost', 
        help='Indicate the ip address to send the data to')
    
    parser.add_argument('-f', type=str, dest='filename', default='', 
        help='Indicate the name of file to send')
    
    args = parser.parse_args()
    
    print("Data rate is %.1f Mbps\nSending to %s" % (args.rate, args.address))
    main(args.rate, args.address, args.filename)



