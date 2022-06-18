from socket import *

if __name__ == "__main__":

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5555))
    print("Server has started")
    expected = 1

    while True:
        data, addrs = sock.recvfrom(4096)
        received = int(data[:5])
        if data:
            print(expected, received)
            if expected != received:
                missing = received - expected
                print("Warning! Missing datagrams!\n")*missing
                expected = received
            else:
                print("Message is received from client")
                expected += 1
