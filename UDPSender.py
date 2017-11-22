#!/usr/bin/python3

"""
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

def send_reply(rate, continuous, address, filename):
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
    while segId < len(message) or continuous:
        if (time.time() - nexttime) < timeinterval: continue
        nexttime += timeinterval
        if not continuous:
            msg = message[segId:segId+4060] # spliced file contents
        else:
            msg = urandom(4060) # junk data
        msg_length = len(msg)
        payload = pack('ii' + str(msg_length) + 's', segId, msg_length, msg) # struct pack is used to make sure that segId is always 4 bytes large, msg_length is always 4 bytes large, since integers in python are always 4 bytes
        sent = sock.sendto(payload, server_address)
        # print('sent %d bytes' % (sent))
        segId += msg_length
        sys.stdout.write("\rTime elapsed: %.3fs" % (time.time()-starttime))
        sys.stdout.flush()
    
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
    send_reply(args.rate, args.continuous, args.address, args.filename)



