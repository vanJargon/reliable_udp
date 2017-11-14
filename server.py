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

def run_server(verbose, savefile, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#socket.SOCK_RAW, socket.IPPROTO_IP)#
    server_address = '0.0.0.0'
    server_port = 5555
    sock.bind((server_address, server_port))
    
    if verbose:
        print("Server started. Listening on %s at port %d" % (server_address, server_port))
    talkedTo = {}
    s = bytearray()
    p_counter = 0
    
    while True:
        recv = sock.recvfrom(65535)
        data, client_addr = recv
        client_ip = client_addr[0]
        msg_length = len(data) - 9
        flags, tr_id, nextSegId, msg = unpack('!BII' + str(msg_length) + 's', data)
        
        if int(nextSegId) == 0:
            print('new filestream started')
        
        # store data into s TODO: make it such that data stored is unique to transaction_id, source_ip and source_port
        s[nextSegId:msg_length] = msg
        
        print('received %d bytes of data from %s' % (len(data), str(client_addr)))
        
        if verbose:
            #print("Data: {}".format(data))
            #print("Addresses: {}".format(client_addr))
            print("%d:%d" % (nextSegId, msg_length))
        
        segId = talkedTo.get(client_ip, -1)
        
        if int(nextSegId) != segId and int(nextSegId) != 0:
            print('error: not in order. waiting for id=%s\n' % (segId))
            continue
        
        talkedTo[client_ip] = int(nextSegId) + int(msg_length)
        
        p_counter += 1
        if p_counter > 10 or flags & 2**1:
            sock.sendto(b'yep', client_addr)
            print('received')
            p_counter = 0
            if savefile and s and flags & 2**1:
                with open(output_file, 'wb') as of:
                    of.write(s)
                s = bytearray()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Prints data and addresses')
    parser.add_argument('-s', '--savefile', action='store_true', default=False, help='Indicate whether to save data to file')
    parser.add_argument('-o', dest='output_file', default='output', help='Indicate name of file to output')
    
    args = parser.parse_args()

    run_server(args.verbose, args.savefile, args.output_file)
        
