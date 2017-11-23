Networks Project
================
A project to implement a reliable and quick transport protocol (RQTP) in a local network, used for Point to point file transfer.

RQTP - Reliable and Quick file Transfer Protocol
------------
For reliable of sending files using our protocol over IP/UDP. 
Written in python3, but also compatible with python2.7

Files: `sender.py`, `receiver.py`
Aux files: `ignite.mp4`, `largefile.txt`

For `sender.py`, 
usage: sender.py [-h] [-r RATE] [-a ADDRESS] [-f FILENAME] [-p PORTNUM]

optional arguments:
`  -h, --help   show this help message and exit
`  -r RATE      Specify starting packet rate in Mbps (eg; -r 1.5 is 1.5 Mbps)
`  -a ADDRESS   Indicate the ip address to send the data to. Default is
`               localhost.
`  -f FILENAME  Indicate the name of file to send
`  -p PORTNUM   Indicate destination port. Default is 5555.

For `receiver.py`, 
usage: receiver.py [-h] [-v] [-s] [-o OUTPUT_FILENAME]

optional arguments:
`  -h, --help          show this help message and exit
`  -v, --verbose       Prints data and addresses
`  -s, --savefile      Indicate whether to save data to file
`  -o OUTPUT_FILENAME  Indicate name of file to output. Defaults to 'output' in
                      the same directory

Simply run `receiver.py` on the host you wish to receive the file and `sender.py` on the host that is sending the file. 

Reliability
------------
Reliability is ensured using our own customization of the Selective Repeat strategy, using what we call a composite window instead. 

The twist is that instead of having a sliding window that waits for the first packet in the window to be ACKed before it can slide, our composite window simply removes ACKed packet and adds new packets to the window as long as the window is not full and the end of message has not been reached. 

This composite window was implemented using a simple python array, accompanied by an equal sized array to act as a timer. 

A while loop is used for busy waiting, both responding to ACKs when they arrive as well as resending packets when their timers expire. 

Finally, when all acknowledgements have been received, a single packet with the f_fin bit flag set indicates that the file has been sent successfully. 


Flow Control
------------
To test UDP in the case of congestion causing data loss. 

Reliability 
Files: `reliableClientTest.py`, `reliableServerTest.py`

Testing reliability using lab3 files by adjusting rates of data transfer. 

Flow Control
Files: `FlowControlClientTest.py`, `FlowControlServerTest.py`

Testing congestion adjustment by varying size of files in accordance to data loss.

Variables involved: 

`mtu`(Integer): the value of a single unit of measurement for packet size.

`factor`(Integer): the value that determines how large the packet size is. 

`packet_size`(Integer): the size of packets to be sent = factor * mtu.

`safeConnect`(Integer): the value that tracks the amount of successful transcation in data transmission. Consecutive successes increases factor, therby increasing packet_size.

`dataLoss`(Integer): Integer number that tracks the amount of timeout from data loss. Consecutive timeouts decreases factor, thereby reducing packet_size. 

Testing with Mininet
----------------------
Mininet is used to simulate a network with packet loss and reordering. 

Files: `topo.py`
Aux files: `TCPReceiver.py`, `TCPSender.py`, `UDPReceiver.py`, `UDPSender.py`

To start mininet, run
```terminal
$ sudo python topo.py --bw-net 3.0 --delay 10 --dir ./ --nflows 1 --maxq 100 -n 5
```

This initializes mininet with the default arguments (used in the tests). By default, 5 hosts are initialized and the bandwidth of each link is set to 3.0 Mbps. Using `netem`, each link in the network is set to have a different loss rate (link between switch `s0` and `h1` has 0% loss, `s0-h2` has 2% loss,..., `s0-h5` has 8% loss) to improve the ease of testing under different circumstances. In addition, the switch is also set to deliberately forward 75% of the packets delayed so that the packets are received at the receiver out of order. 

In the testing procedure, the node `h1` is set as the sender, and the nodes `h2`,...,`h5` the receiver. All 3 protocols (TCP, UDP, RQTP) are tested in the same setup and the time taken to transmit the same file is recorded. The integrity of the file is also checked at the end of each transmission. 
