#!/usr/bin/python2

"""
Networks Lab 3: UDP Socket Programming

Server code.
"""

from socket import *

if __name__ == "__main__":

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('localhost', 5555))

    while True:
        data, addrs = sock.recvfrom(4096)
        segment_id, segment = data.split(':',1)
        segment_id = int(segment_id)

        if segment_id == -1: # special segment ID for new data sequence
            print('New sequence of data started with client {}!'.format(addrs))
            segment = int(segment)
            waitingSegments = range(segment)
            receivedSegments = [None] * segment
            lastSegmentID = segment - 1
            sock.sendto('OK', addrs)
            print 'Receiving from client...'

        elif segment_id >= 0: # normal segments containing message
            waitingSegments.remove(segment_id)
            receivedSegments[segment_id] = segment

            # check if this is the last segment transmitted.
            if segment_id == lastSegmentID:
                if waitingSegments:
                    print '===============ERROR==============='
                    print 'Missing datagrams: %s' % (','.join(map(str,waitingSegments)))
                else:
                    print '===========BEGIN MESSAGE==========='
                    print ' '.join(receivedSegments)
                    print '============END MESSAGE============'
                    print 'Received all data from client.'
