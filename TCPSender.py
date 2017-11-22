#socket_echo_client.py
import socket
import sys
import time
import argparse

def main(rate, address, filename):
    if filename:
        with open(filename, 'rb') as input_file:
            message = input_file.read()
    else:
        message = 'hi how are you'.encode('UTF-8')    

    starttime = time.time()
    

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
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
    parser.add_argument('-r', type=float, dest='rate', default=3.0, 
        help='Packet rate in Mbps (eg; -r 1.5 is 1.5 Mbps)')
    
    parser.add_argument('-a', type=str, dest='address', default='localhost', 
        help='Indicate the ip address to send the data to')
    
    parser.add_argument('-f', type=str, dest='filename', default='', 
        help='Indicate the name of file to send')
    
    args = parser.parse_args()
    
    print("Data rate is %.1f Mbps\nSending to %s" % (args.rate, args.address))
    main(args.rate, args.address, args.filename)