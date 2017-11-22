#!/usr/bin/python

"50.012 Networks Project Mininet Congestion Simulation"

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.node import OVSController

from subprocess import Popen
from argparse import ArgumentParser

# Parse arguments

parser = ArgumentParser(description="Congestion Simulation tests")
parser.add_argument('--bw-net', '-b',
                    dest="bw_net",
                    type=float,
                    action="store",
                    help="Bandwidth of network link",
                    required=True)

parser.add_argument('--delay',
                    dest="delay",
                    type=float,
                    help="Delay in milliseconds of host links",
                    default=10)

parser.add_argument('--dir', '-d',
                    dest="dir",
                    action="store",
                    help="Directory to store outputs",
                    default="results",
                    required=True)

parser.add_argument('-n',
                    dest="n",
                    type=int,
                    action="store",
                    help="Number of nodes in star.",
                    required=True)

parser.add_argument('--nflows',
                    dest="nflows",
                    action="store",
                    type=int,
                    help="Number of flows per host (for TCP)",
                    required=True)

parser.add_argument('--maxq',
                    dest="maxq",
                    action="store",
                    help="Max buffer size of network interface in packets",
                    default=500)

parser.add_argument('--cong',
                    dest="cong",
                    help="Congestion control algorithm to use",
                    default="reno")
parser.add_argument('--diff',
                    help="Enabled differential service", 
                    action='store_true',
                    dest="diff",
                    default=False)

# Expt parameters
args = parser.parse_args()

class StarTopo(Topo):
    "Star topology for Congestion Simulation experiment"

    def __init__(self, n=2, cpu=None, bw_host=1000, bw_net=1.5,
                 delay='10', maxq=None, diff=False):
        # Add default members to class.
        super(StarTopo, self ).__init__()

        # Create switch and host nodes
        for i in xrange(n):
            self.addHost( 'h%d' % (i+1), cpu=cpu )

        self.addSwitch('s0', fail_mode='open')

        for i in xrange(0, n):
            link_loss = i*(10/n) # h1 (i=0) will have 0% link loss, limit link loss is 50%
            self.addLink('h%d' % (i+1), 's0', bw=bw_net, loss=link_loss)

def configureNetwork(net, n, switchNode='s0'):
    switch = net.getNodeByName(switchNode)
    
    for i in xrange(0, n):
        linkLoss = i*(10/n) # h1 (i=0) will have 0% link loss, limit link loss is 50%
        cmd = 'tc qdisc change dev %s-eth%d parent 5:1 netem delay 10ms reorder 25%% 50%% loss %d%%' % (switchNode, (i+1), linkLoss) # 25% of packets (with a correlation of 50%) will get send immediately, others will be delayed by 10ms
        switch.cmd(cmd)

def main():
    "Create network and run Congestion Simulation experiment"
    print "starting mininet ...."
    # Reset to known state
    topo = StarTopo(n=args.n, delay='%sms' % args.delay,
                    bw_net=args.bw_net, maxq=args.maxq, diff=args.diff)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink,
                  autoPinCpus=True, controller=OVSController)
    net.start() #starts lossy network
    print "net started"
    configureNetwork(net, args.n)
    print "packet reordering and loss enabled"
    dumpNodeConnections(net.hosts)
    #net.pingAll()
    CLI(net)
    Popen('killall -9 cat', shell=True).wait()

if __name__ == '__main__':
    main()
