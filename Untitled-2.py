#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
import os

class LinuxRouter( Node ):

    # pylint: disable=arguments-differ
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class NetworkTopo( Topo ):

    # pylint: disable=arguments-differ
    def build( self, **_opts ):

        r1 = self.addNode( 'r1', cls = LinuxRouter, ip = '192.168.1.1' )
        r2 = self.addNode( 'r2', cls = LinuxRouter, ip = '192.168.2.1' )
        r3 = self.addNode( 'r3', cls = LinuxRouter, ip = '192.168.3.1' )
        r4 = self.addNode( 'r4', cls = LinuxRouter, ip = '192.168.4.1' )
        
        h1 = self.addHost( 'h1', ip = '192.168.1.2' )
        h2 = self.addHost( 'h2', ip = '192.168.3.2' )

        self.addLink( r1, h1, intfName1 = 'r1-eth0', intfName2 = 'h1-eth0',
            cls = TCLink, bw = 1,
            params1 = { 'ip' : '192.168.1.1/24' }, params2 = { 'ip' : '192.168.1.2/24' } )
        self.addLink( r2, h1, intfName1 = 'r2-eth0', intfName2 = 'h1-eth1',
            cls = TCLink, bw = 1,
            params1 = { 'ip' : '192.168.2.1/24' }, params2 = { 'ip' : '192.168.2.2/24' } )

        self.addLink( r3, h2, intfName1 = 'r3-eth0', intfName2 = 'h2-eth0',
            cls = TCLink, bw = 1,
            params1 = { 'ip' : '192.168.3.1/24' }, params2 = { 'ip' : '192.168.3.2/24' } )
        self.addLink( r4, h2, intfName1 = 'r4-eth0', intfName2 = 'h2-eth1',
            cls = TCLink, bw = 1,
            params1 = { 'ip' : '192.168.4.1/24' }, params2 = { 'ip' : '192.168.4.2/24' } )

        self.addLink( r1, r3, intfName1 = 'r1-eth1', intfName2 = 'r3-eth1',
            cls = TCLink, bw = 0.5,
            params1 = { 'ip' : '10.0.1.1/24' }, params2 = { 'ip' : '10.0.1.2/24' } )
        self.addLink( r1, r4, intfName1 = 'r1-eth2', intfName2 = 'r4-eth1',
            cls = TCLink, bw = 1,
            params1 = { 'ip' : '10.0.2.1/24' }, params2 = { 'ip' : '10.0.2.2/24' } )

        self.addLink( r2, r3, intfName1 = 'r2-eth1', intfName2 = 'r3-eth2',
            cls = TCLink, bw = 1,
            params1 = { 'ip' : '10.0.3.1/24' }, params2 = { 'ip' : '10.0.3.2/24' } )
        self.addLink( r2, r4, intfName1 = 'r2-eth2', intfName2 = 'r4-eth2',
            cls = TCLink, bw = 0.5,
            params1 = { 'ip' : '10.0.4.1/24' }, params2 = { 'ip' : '10.0.4.2/24' } )

def run():
    topo = NetworkTopo()
    net = Mininet( topo = topo, host = CPULimitedHost, link = TCLink, waitConnected = True )
    net.start()

    h1, h2, r1, r2, r3, r4 = net.get( 'h1', 'h2', 'r1', 'r2', 'r3', 'r4' )

    r1.cmd( 'ip route add 10.0.3.0/24 via 10.0.1.2 dev r1-eth1' )
    r1.cmd( 'ip route add 192.168.2.1 via 10.0.1.2 dev r1-eth1' )
    r1.cmd( 'ip route add 192.168.3.0/24 via 10.0.1.2 dev r1-eth1' )
    r1.cmd( 'ip route add 192.168.4.0/24 via 10.0.2.2 dev r1-eth2' )

    r2.cmd( 'ip route add 10.0.1.0/24 via 10.0.3.2 dev r2-eth1' )
    r2.cmd( 'ip route add 192.168.1.1 via 10.0.3.2 dev r2-eth1' )
    r2.cmd( 'ip route add 192.168.3.0/24 via 10.0.3.2 dev r2-eth1' )
    r2.cmd( 'ip route add 192.168.4.0/24 via 10.0.4.2 dev r2-eth2' )

    r3.cmd( 'ip route add 10.0.2.0/24 via 10.0.1.1 dev r3-eth1' )
    r3.cmd( 'ip route add 192.168.1.0/24 via 10.0.1.1 dev r3-eth1' )
    r3.cmd( 'ip route add 192.168.2.0/24 via 10.0.3.1 dev r3-eth2' )
    r3.cmd( 'ip route add 192.168.4.1 via 10.0.1.1 dev r3-eth1' )

    r4.cmd( 'ip route add 10.0.1.0/24 via 10.0.2.1 dev r4-eth1' )
    r4.cmd( 'ip route add 192.168.1.0/24 via 10.0.2.1 dev r4-eth1' )
    r4.cmd( 'ip route add 192.168.2.0/24 via 10.0.4.1 dev r4-eth2' )
    r4.cmd( 'ip route add 192.168.3.1 via 10.0.2.1 dev r4-eth1' )

    h1.cmd( 'ip route add 192.168.3.0/24 via 192.168.1.1 dev h1-eth0' )
    h1.cmd( 'ip route add 192.168.4.0/24 via 192.168.2.1 dev h1-eth1' )
    h1.cmd( 'ip route add default scope global nexthop via 192.168.1.1 dev h1-eth0')
    h2.cmd( 'ip route add 192.168.1.0/24 via 192.168.3.1 dev h2-eth0' )
    h2.cmd( 'ip route add 192.168.2.0/24 via 192.168.4.1 dev h2-eth1' )
    h2.cmd( 'ip route add default scope global nexthop via 192.168.3.1 dev h2-eth0')

    net.pingAll()
    CLI( net )
    net.stop()

topos = { 'mytopo': NetworkTopo }
tests = { 'mytest': run }

if __name__ == '__main__':
    os.system( 'mn -c' ); os.system( 'clear' )
    # setLogLevel( 'info' )
    run()