#!/usr/bin/python3
import socket
import sys
import argparse

def main(verbose, savefile, output_filename):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('0.0.0.0', 10000)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)
    
    s = bytearray()

    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            # print('connection from', client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                s += data
                # print('received {!r}'.format(data))
                if data:
                    # print('sending data back to the client')
                    connection.sendall(data)
                else:
                    # print('no data from', client_address)
                    break

        finally:
            # Clean up the connection
            print("File Transfer Complete")
            connection.close()
            if savefile:
                with open(output_filename, 'wb') as of:
                    of.write(s)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Prints data and addresses')
    parser.add_argument('-s', '--savefile', action='store_true', default=False, help='Indicate whether to save data to file')
    parser.add_argument('-o', dest='output_filename', default='output', help="Indicate name of file to output. Defaults to 'output' in the same directory")
    
    args = parser.parse_args()

    main(args.verbose, args.savefile, args.output_filename)