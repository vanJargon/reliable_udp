Networks Project
================
A project to implement a reliable and quick transport protocol (RQTP) in a local network, used for:
- Point to point file transfer
- Broadcasting

Testing and Experiment
----------------------
Mininet is used to simulate our network with packet loss. 

To start mininet, use
```terminal
$ sudo ./run.sh
```

The `run.sh` file specifies the default arguments that will be used when initializing mininet. By default, 5 hosts are initialized and the bandwidth of each link is set to 1.5 Mbps. Each link in the network has a different loss (h1 has 0% loss, h2 has 20% loss,..., h5 has 80% loss) to test the reliability of our file transfer protocol.

To test the reliability of the protocol, start the server application on h1 and the client(s) on h2-h5 and proceed with the file transfer. 

Flow Control
------------
To test UDP in the case of congestion causing data loss. 

Reliability 
Files: reliableClientTest.py, reliableServerTest.py

Testing reliability using lab3 files by adjusting rates of data transfer. 

Flow Control
Files: FlowControlClientTest.py, FlowControlServerTest.py

Testing congestion adjustment by varying size of files in accordance to data loss. 
