import datetime, time
from socket import *

for pings in range(10):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)
    message = "test"
    addr = ("127.0.0.1", 12000)

    start = datetime.datetime.now()
    clientSocket.sendto(message.encode(), addr)
    try:
        data, server = clientSocket.recvfrom(1024)
        end = datetime.datetime.now()
        elapsed = end - start
        print('%s %d %d' % (data, pings, elapsed.microseconds))
        time.sleep(1)
    except timeout:
        print("REQUEST TIMED OUT")
        time.sleep(1)