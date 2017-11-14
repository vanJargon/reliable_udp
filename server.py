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
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW)
    sock.bind(('0.0.0.0', 5555))
    
    talkedTo = {}
    
    while True:
        data = sock.recvfrom(4096)
        print(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Prints data and addresses')
    
    args = parser.parse_args()

    run_server(args.verbose)
        
