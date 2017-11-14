#!/usr/bin/python3

"""
Networks Lab 3: UDP Socket Programming
Name: Jonathan Wee (1001458)
Name: Vanessa Tan (1001827)

Server code.

Socket binds to 0.0.0.0 instead of localhost so it responds to its public IP address

New filestreams must start with segId=0
Subsequent segIds simply add the current segId and the number of msg bytes received
If UDP packets are received in order, no output is given
Else, server will print error message

Additional cmd line option --verbose added to make server noisy
"""

import socket
from struct import *
import argparse

def run_server(verbose):
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)#SOCK_DGRAM)#
    sock.bind(('0.0.0.0', 5555))
    
    talkedTo = {}
    s = bytearray()
    
    while True:
        if verbose:
            print("waiting for data")
        recv = sock.recvfrom(65535)
        data, addrs = recv
        print('received %d bytes of data from %s' % (len(data), str(addrs)))
        #continue
        l = len(data) - 36
        stuff, nextSegId, msg_length, msg = unpack('!28sii' + str(l) + 's', data)
        ipheader,cport,sport,mlen,chksum = unpack('!20sHHHH', stuff)
        
        if int(nextSegId) == 0:
            print('new filestream started')
            with open('output', 'wb') as output_file:
                output_file.write(s)
            s = bytearray()
        s[nextSegId:msg_length] = msg
        
        if verbose:
            #print("Data: {}".format(data))
            #print("Addresses: {}".format(addrs))
            print("%d:%d" % (nextSegId, msg_length))
        
        segId = talkedTo.get(addrs[0], -1)
        
        if int(nextSegId) != segId and int(nextSegId) != 0:
            print('error: not in order. waiting for id=%s\n' % (segId))
            continue
        
        #sock.sendto('yep', addrs)
        talkedTo[addrs[0]] = int(nextSegId) + int(msg_length)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Prints data and addresses')
    
    args = parser.parse_args()

    run_server(args.verbose)
        
