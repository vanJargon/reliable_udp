#!/usr/bin/python3

"""
Server code.

Socket binds to 0.0.0.0 instead of localhost so it responds to its public IP address

As our protocol runs on top of UDP, we have the following structure
Header layout
|f_nack(4bits)|f_fin(1bit)|f_ack(1bit)|f_endTransaction(1bit)|f_newTransaction(1bit)|transactionId(4bytes)|segId(4bytes)|data|

New filestreams must start with segId=0, with f_newTransaction=1
Subsequent segIds simply add the current segId and the number of msg bytes received

The server either acks or nacks every 10 messages received from the same IP,Port,TransactionId

Additional cmd line option --verbose added to make server noisy
"""

import socket
from struct import *
import argparse
from sortedcontainers import SortedList

def run_server(verbose, savefile, output_filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#socket.SOCK_RAW, socket.IPPROTO_IP)#
    server_address = '0.0.0.0'
    server_port = 5555
    sock.bind((server_address, server_port))
    
    if verbose:
        print("Server started. Listening on %s at port %d" % (server_address, server_port))
    talkedTo = {}
    s = bytearray()
    segIdTracker = SortedList([0])
    p_counter = 0
    
    while True:
        recv = sock.recvfrom(65535)
        data, client_addr = recv
        client_ip = client_addr[0]
        msg_length = len(data) - 9
        flags, tr_id, segId, msg = unpack('!BII' + str(msg_length) + 's', data)
        
        f_newTransaction = flags & 2**0
        if f_newTransaction:
            print('new filestream started')
            s = bytearray()
            segIdTracker = SortedList([0])
        
        # store data into s TODO: make it such that data stored is unique to transaction_id, source_ip and source_port
        s[segId:msg_length] = msg
        
        if segId == segIdTracker[0]:
            segIdTracker.remove(segId)
            segIdTracker.add(segId+msg_length)
        else:
            segIdTracker.add(segId)
            segIdTracker.add(segId+msg_length)
        #if segId+msg_length in segIdTracker:
        #    segIdTracker.remove(segId+msg_length)
        #    if segId in segIdTracker:
        #        segIdTracker.remove(segId)
        #elif segId in segIdTracker:
        #    segIdTracker.remove(segId)
        #    segIdTracker.add(segId+msg_length)
        #elif segId+msg_length > segIdTracker[0]:
        #    segIdTracker.remove(segIdTracker[0])
        #    segIdTracker.add(segId+msg_length)
        #else:
        #    segIdTracker.add(segId+msg_length)
            
        
        
        print('received %d bytes of UDP payload from %s' % (len(data), str(client_addr)))
        
        if verbose:
            #print("Data: {}".format(data))
            #print("Addresses: {}".format(client_addr))
            print("%d:%d" % (segId, msg_length))
        
        talkedTo[client_ip] = int(segId) + int(msg_length)
        
        f_endTransaction = flags & 2**1
        p_counter += 1
        if p_counter > 10 or f_endTransaction:
            unreceivedIds = [i for i in segIdTracker if i != segId+msg_length]
            f_nack = 1 if unreceivedIds else 0
            f_newTransaction = 0
            f_endTransaction = 0
            f_ack = 0
            if f_nack:
                f_fin = 0
                flags = f_newTransaction + (f_endTransaction << 1) + (f_ack << 2) + (f_fin << 3) + (f_nack << 4)
                pp = '!BI'# + 'I'*len(unreceivedIds)
                payload = pack(pp, flags, unreceivedIds[0])
                sock.sendto(payload, client_addr)
            else:
                f_fin = 1
                flags = f_newTransaction + (f_endTransaction << 1) + (f_ack << 2) + (f_fin << 3) + (f_nack << 4)
                payload = pack('!B', flags)
                sock.sendto(payload, client_addr)
            print('sent',payload,'to',client_addr)
            print('received %d bytes of actual data in total' % (len(s)))
            p_counter = 0
        if f_endTransaction and savefile:
            with open(output_filename, 'wb') as of:
                of.write(s)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Prints data and addresses')
    parser.add_argument('-s', '--savefile', action='store_true', default=False, help='Indicate whether to save data to file')
    parser.add_argument('-o', dest='output_filename', default='output', help="Indicate name of file to output. Defaults to 'output' in the same directory")
    
    args = parser.parse_args()

    run_server(args.verbose, args.savefile, args.output_filename)
        
