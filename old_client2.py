#!/usr/bin/python2

"""
Networks Lab 3: UDP Socket Programming

Client code.
"""
from socket import *
import argparse
import datetime
import time

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=float, dest='rate',
        help='Packet rate in Mbps (eg; -r 1.5 is 1.5 Mbps)')
    # add optional argument for message to server
    parser.add_argument('-m', type=str, dest='message',
        help='Message to send to server (eg; -m "This is the message from the client"')

    args = parser.parse_args()

    if args.rate == None:
        print("USAGE:")
        print("python2 client.py -r 3.0")
    else:
        print("Client rate is {} Mbps.".format(args.rate))

        if args.message:
            message = args.message
        else:
            with open('largeFile.txt','r') as input_file:
                message = input_file.read().replace('\n','')
        
        ''' 1. SET UP SOCKET '''
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('localhost',0)) # socket binds to a free port
        print 'Client binded to port %s.' % (sock.getsockname()[1]) # this instance of client.py will only use this port number
        server_address = ('localhost', 5555)

        ''' 2. SPLIT MESSAGE INTO EQUAL SIZED SEGMENTS TO BE SENT '''      
        segment_size = 512
        packets = ['%s' % message[i:i+segment_size] for i in range(0, len(message), segment_size)]
        packets[-1] = packets[-1] + "\x00"*(len(message)%segment_size)

        ''' 3. INITIATE CONNECTION WITH SERVER AND AWAIT SERVER REPLY. IF NO REPLY, TIMEOUT '''
        print 'Initiating connecting with server...'
        sock.sendto('-1:%d'%(len(packets)), server_address)
        print 'Awaiting reply from server...'
        sock.settimeout(5.0)
        data, addrs = sock.recvfrom(4096)
        if data == 'OK':
            sock.settimeout(None)
            print 'Received reply from server: %s' % (data)
            print 'Beginning message transmission...'
            start = datetime.datetime.utcnow()
            for i in range(len(packets)): 
                payload = str(i)+':'+packets[i]
                interval = (sock.sendto(payload, server_address))/(args.rate*1000000)
                time.sleep(interval)
            end = datetime.datetime.utcnow()
            total_time = (end-start).total_seconds()

            print 'Finished sending message to server.'
            print '===========STATISTICS==========='
            print 'Start time: ' + str(start)
            print 'End time: ' + str(end)
            print 'Total time taken: %f s'%(total_time)
