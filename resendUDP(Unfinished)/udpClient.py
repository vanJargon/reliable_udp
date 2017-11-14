from socket import *
import argparse
import time


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=float, dest='rate',
                        help='Packet rate in Mbps (eg; -r 1.5 is 1.5 Mbps)')

    args = parser.parse_args()
    count = 0

    if args.rate == None:
        print("USAGE:")
        print("python2 client.py -r 3.0:")
    else:
        print("Client rate is {} Mbps.".format(args.rate))
        max_count = args.rate*1000
        mail = "HELLOWORLD"*99 + "Hello"
        seg_id = '%05d'%1
        wait = 1/max_count
        check_size = 0
        print(max_count, wait)
        start_time = time.time()
        while count!=max_count:
            sock = socket(AF_INET, SOCK_DGRAM)
            server_address = ('10.0.0.2', 5555)
            message = seg_id + mail
        sent = sock.sendto(message, server_address)
        print(seg_id)
        check_size += sent
        seg_id = '%05d'%(int(seg_id) + 1)
        count += 1
        time.sleep(wait)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Total bytes sent to server: " + str(check_size))
    print("Total elapsed time: " + str(elapsed_time))



