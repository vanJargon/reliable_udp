#!/usr/bin/python3

"""
Networks Lab 3: UDP Socket Programming
Name: Jonathan Wee (1001458)
Name: Vanessa Tan (1001827)

Client code.

Packet layout
|IP header (20bytes)|UDP header (8bytes)|Payload|

Payload layout
|segId(4bytes)|msg_length(4bytes)|data|

Assuming server only receives 4096 bytes at a time. 
Max data size = 4096 - 8 - 20 - 4 - 4 = 4060

1.0Mbps = 125kBps
Sending packets of size 4096Bytes, we have to send a packet every 4096B/(1.0*125000Bps) = 0.032768 seconds
Or, time interval between packets = 4096B/(rate*125000Bps)

Use -r to select rate
Use -c to make continuous stream of junk data
Use -a to select address to send data to, default is localhost

On mininet, to send data to another host, please use -a <other host IP>, e.g. python ./lab3client.py -r 3 -a 10.0.0.2
"""

from socket import *
import argparse
from os import urandom
from struct import *
import time
import sys

def main(rate, continuous, address, filename):
    sock = socket(AF_INET, SOCK_DGRAM)
    server_address = (address, 5555)
    if filename:
        with open(filename, 'rb') as input_file:
            message = input_file.read()
    else:
        message = 'hi how are you'.encode('UTF-8')
    
    starttime = time.time()
    
    timeinterval = 4096.0/(rate*125000)
    
    nexttime = starttime - timeinterval # to make the client start sending data immediately instead of waiting for timeinterval
    
    segId = 0
    tr_id = 353 # should be random
    p_counter = 0
    while segId < len(message) or continuous:
        if (time.time() - nexttime) < timeinterval: continue
        nexttime += timeinterval
        
        if not continuous:
            msg = message[segId:segId+65498] # spliced file contents
        else:
            msg = urandom(4060) # junk data
        msg_length = len(msg)
        f_newTransaction = 1 if segId == 0 else 0
        f_endTransaction = 1 if segId+65498 >= len(message) else 0
        f_ack = 0
        f_fin = 0
        f_nack = 0
        flags = f_newTransaction + (f_endTransaction << 1) + (f_ack << 2) + (f_fin << 3) + (f_nack << 4)
        #print(flags)
        #print('msg length %d' % msg_length)
        payload = pack('!BII' + str(msg_length) + 's', flags, tr_id, segId, msg) # struct pack is used to make sure that segId is always 4 bytes large, since integers in python are always 4 bytes
        sent = sock.sendto(payload, server_address)

        #print('sent %d bytes' % (sent))
        segId += msg_length
        sys.stdout.write("\rTime elapsed: %.3fs" % (time.time()-starttime))
        sys.stdout.flush()
        
        p_counter += 1
        if p_counter > 10:
            data, addr = sock.recvfrom(1024)
            p_counter = 0
    
    if p_counter:
        data, addr = sock.recvfrom(1024) 
        print("\nreceived message:", data)
    
if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=float, dest='rate', default=3.0, 
        help='Packet rate in Mbps (eg; -r 1.5 is 1.5 Mbps)')
    
    parser.add_argument('-c', '--continuous', action='store_true', default=False, 
        help='Indicate whether to send a continuous stream of (junk) data')
    
    parser.add_argument('-a', type=str, dest='address', default='localhost', 
        help='Indicate the ip address to send the data to')
    
    parser.add_argument('-f', type=str, dest='filename', default='', 
        help='Indicate the name of file to send')
    
    args = parser.parse_args()
    
    print("Client rate is %.1f Mbps\nContinuous stream = %s" % (args.rate, args.continuous))
    main(args.rate, args.continuous, args.address, args.filename)



