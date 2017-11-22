#!/usr/bin/python3
import socket
import sys
import time
import argparse

def main(address, filename):
    if filename:
        with open(filename, 'rb') as input_file:
            message = input_file.read()
    else:
        message = 'hi how are you'.encode('UTF-8')    

    starttime = time.time()
    

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (address, 10000)
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)

    try:

        # Send data
        # message = b'This is the message.  It will be repeated.'
        
        # print('sending {!r}'.format(message))
        sock.sendall(message)

        # Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            # print('received {!r}'.format(data))

    finally:
        print('closing socket')
        sock.close()
        elapsedtime = time.time() - starttime
        print(elapsedtime)

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-a', type=str, dest='address', default='localhost', 
        help='Indicate the ip address to send the data to')
    
    parser.add_argument('-f', type=str, dest='filename', default='', 
        help='Indicate the name of file to send')
    
    args = parser.parse_args()
    
    print("Sending to %s" % (args.address))
    main(args.address, args.filename)