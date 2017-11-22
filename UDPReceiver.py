#!/usr/bin/python3

"""
Socket binds to 0.0.0.0 instead of localhost so it responds to its public IP address

New filestreams must start with segId=0
Subsequent segIds simply add the current segId and the number of msg bytes received
If UDP packets are received in order, no output is given
Else, server will print error message

Additional cmd line option --verbose added to make server noisy
"""

from socket import *
from struct import *
import argparse

def run_server(verbose=0):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5555))
    
    talkedTo = {}
    
    while True:
        if verbose:
            print("waiting for data")
        data, addrs = sock.recvfrom(4096)
        l = len(data) - 8
        nextSegId, msg_length, msg = unpack('ii' + str(l) + 's', data)
        
        if int(nextSegId) == 0:
            print('new filestream started')
        
        if verbose:
            #print("Data: {}".format(data))
            #print("Addresses: {}".format(addrs))
            print("%d:%d" % (nextSegId, msg_length))
        
        segId = talkedTo.get(addrs[0], -1)
        
        if int(nextSegId) != segId and int(nextSegId) != 0:
            print('error: not in order. waiting for id=%s\n' % (segId))
            continue
        
        talkedTo[addrs[0]] = int(nextSegId) + int(msg_length)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Prints data and addresses')
    
    args = parser.parse_args()

    run_server(args.verbose)
        
