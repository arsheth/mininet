"""
Example topology of Quagga routers
"""

import inspect
import os
from mininext.topo import Topo
from mininext.node import Host
from mininext.services.quagga import QuaggaService
from mininet.node import Node, Controller, RemoteController
from mininet.cli import CLI
from collections import namedtuple
from mininet.net import Mininet
from mininet.log import setLogLevel, info, debug

#QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
class QuaggaHost(Host):
	def __init__(self, name, ip, route, *args, **kwargs):
		Host.__init__(self, name, ip=ip, *args, **kwargs)
		self.route = route
	def config(self, **kwargs):
		Host.config(self, **kwargs)
		debug("configuration route %s" % self.route)
		self.cmd('ip route add default via %s' %self.route)
net = None
QUAGGA_RUN_DIR = '/var/run/quagga'
QUAGGA_DIR = '/usr/lib/quagga'
CONFIG_DIR = 'configs'

class Router(Host):
	def __init__(self,name,quaggaConfFile, intfDict, *args, **kwargs):
		Host.__init__(self, name, *args, **kwargs)
		self.quaggaConfFile = quaggaConfFile
		#self.zebraConfFile = zebraCongFile
		self.intfDict = intfDict
	#	self.dests = dests
	#	self.ports = ports
	#	self.gws = gws
	
	def config(self, **kwargs):
		Host.config(self, **kwargs)
		self.cmd('sysctl net.ipv4.ip_forward=1')

		for intf,attrs in self.intfDict.items():
			self.cmd('ip addr flush dev %s' % intf)
			if 'mac' in attrs:
				self.cmd('ip link set %s down' % intf)
				self.cmd('ip link set %s address %s' % (intf, attrs['mac']))
				self.cmd('ip link set %s up' % intf)
			for addr in attrs['ipAddrs']:
				self.cmd('ip addr add %s dev %s' % (addr, intf))
		self.cmd('usr/lib/quagga/bgpd -d -f %s -z %s/zebra%s.api -i %s/bgpd%s.pid' % (self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
		#for i in range(len(self.dests)):
		#	print self.dests[i]
		#	self.cmd('route add -net %s gw %s netmask 255.255.255.0 %s' %(self.dests[i],self.gws[i],self.ports[i]))
  
	def terminate(self):
		Host.terminate(self)

class QuaggaTopo(Topo):

    "Creates a topology of Quagga routers"

    def __init__(self):
        """Initialize a Quagga topology with 5 routers, configure their IP
           addresses, loop back interfaces, and paths to their private
           configuration directories."""
        Topo.__init__(self)

        # Directory where this file / script is located"
        selfPath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))  # script directory

        # Initialize a service helper for Quagga with default options
        quaggaSvc = QuaggaService(autoStop=False)

        # Path configurations for mounts
        quaggaBaseConfigPath = selfPath + '/configs/'

        # List of Quagga host configs
	h1 = self.addHost('h1', cls=QuaggaHost,ip='150.100.1.11/24',route='150.100.1.254')
#	print self
#	self.cmd('h1 route add deault gw 150.100.1.254') 
	h2 = self.addHost('h2', cls=QuaggaHost,ip='150.100.2.12/24', route='150.100.2.254')
#	h2.cmd('route add default gw 150.100.2.254')

	eth0 = { 'mac' : '00:00:00:01:01',
		 'ipAddrs' : ['150.100.1.254/24'] }
	eth1 = { 'ipAddrs' : ['172.16.1.1/24'] }
	eth2 = { 'ipAddrs' : ['172.16.2.1/24'] }
	intfs =  { 'r1-eth0': eth0,
		   'r1-eth1': eth1,
		   'r1-eth2': eth2}
	quaggaConf = '%s/quagga1.conf' % (CONFIG_DIR)
	dests = ['150.100.2.0','150.100.2.0']
	gws = ['172.16.1.254','172.16.2.254']
	ports = ['r1-eth1','r1-eth2']
	r1 = self.addHost('r1', cls=Router, quaggaConfFile=quaggaConf,intfDict = intfs) #, dests=dests,gws=gws,ports=ports)
#	r1.cmd('route add -net 150.100.2.0 gw 172.16.1.254 netmask 255.255.255.0 r1-eth1')	
#	r1.cmd('route add -net 150.100.2.0 gw 172.16.2.254 netmask 255.255.255.0 r1-eth2')
	
	eth0 = { 'mac' : '00:00:00:02:01',
		 'ipAddrs' : ['172.16.1.254/24'] }
	eth1 = { 'ipAddrs' : ['172.16.3.1/24'] }
	intfs =  { 'r2-eth0': eth0,
		   'r2-eth1': eth1}
	quaggaConf = '%s/quagga2.conf' % (CONFIG_DIR)
	
	dests = ['150.100.2.0','150.100.1.0']
	gws = ['172.16.3.254','172.16.1.1']
	ports = ['r2-eth1','r2-eth0']
	r2 = self.addHost('r2', cls=Router, quaggaConfFile=quaggaConf,intfDict = intfs) #,dests=dests,gws=gws,ports=ports)
#	r2.cmd('route add -net 150.100.2.0 gw 172.16.3.254 netmask 255.255.255.0 r2-eth1')
#	r2.cmd('route add -net 150.100.1.0 gw 172.16.1.1 netmask 255.255.255.0 r2-eth0')
	
	
	eth0 = { 'mac' : '00:00:00:03:01',
		 'ipAddrs' : ['172.16.2.254/24'] }
	eth1 = { 'ipAddrs' : ['172.16.4.1/24'] }
	intfs =  { 'r3-eth0': eth0,
		   'r3-eth1': eth1}
	quaggaConf = '%s/quagga3.conf' % (CONFIG_DIR)
	
	dests = ['150.100.2.0','150.100.1.0']
	gws = ['172.16.4.254','172.16.2.1']
	ports = ['r3-eth1','r3-eth0']
	r3 = self.addHost('r3', cls=Router,quaggaConfFile=quaggaConf,intfDict = intfs)#,dests=dests,gws=gws,ports=ports)
	#r3.cmd('route add -net 150.100.2.0 gw 172.16.4.254 netmask 255.255.255.0 r3-eth1')
	#r3.cmd('route add -net 150.100.1.0 gw 172.16.2.1 netmask 255.255.255.0 r3-eth0')
	
	
	eth1 = { 'ipAddrs' : ['172.16.4.254/24'] }
	eth0 = { 'mac' : '00:00:00:04:01',
		 'ipAddrs' : ['172.16.3.254/24'] }
	eth2 = { 'ipAddrs' : ['150.100.2.254/24'] }
	intfs =  { 'r4-eth0': eth0,
		   'r4-eth1': eth1,
		   'r4-eth2': eth2}
	quaggaConf = '%s/quagga4.conf' % (CONFIG_DIR)
#	dests = ['150.100.1.0','150.100.1.0']
#	gws = ['172.16.2.1','172.16.4.1']
#	ports = ['r4-eth0','r4-eth1']
	r4 = self.addHost('r4', cls=Router,quaggaConfFile=quaggaConf,intfDict = intfs) #,dests=dests,gws=gws,ports=ports)
	#r4.cmd('route add -net 150.100.1.0 gw 172.16.2.1 netmask 255.255.255.0 r4-eth0')
	#r4.cmd('route add -net 150.100.1.0 gw 172.16.4.1 netmask 255.255.255.0 r4-eth1')
	
	
	'''
        quaggaHosts = []
        quaggaHosts.append(QuaggaHost(name='h1', ip='192.168.1.1/24',
                                     loIP = '127.0.0.1'))
        quaggaHosts.append(QuaggaHost(name='h2', ip='192.168.2.100/16',
                                      loIP='127.0.0.1'))
        quaggaHosts.append(QuaggaHost(name='r1'))
        quaggaHosts.append(QuaggaHost(name='r2'))
        quaggaHosts.append(QuaggaHost(name='r3'))
        quaggaHosts.append(QuaggaHost(name='r4'))
	'''
	self.addLink(h1,r1)
	self.addLink(r1,r2)
	self.addLink(r1,r3)
	self.addLink(r2,r4)
	self.addLink(r3,r4)
	self.addLink(r4,h2)
        # Add switch for IXP fabric
        #ixpfabric = self.addSwitch('fabric-sw1')

        # Setup each Quagga router, add a link between it and the IXP fabric
    '''    for host in quaggaHosts:

            # Create an instance of a host, called a quaggaContainer
            quaggaContainer = self.addHost(name=host.name,
                                           ip=host.ip,
                                           hostname=host.name,
                                           privateLogDir=True,
                                           privateRunDir=True,
                                           inMountNamespace=True,
                                           inPIDNamespace=True,
                                           inUTSNamespace=True)

            # Add a loopback interface with an IP in router's announced range
            self.addNodeLoopbackIntf(node=host.name, ip=host.loIP)

            # Configure and setup the Quagga service for this node
            quaggaSvcConfig = \
                {'quaggaConfigPath': quaggaBaseConfigPath + host.name}
            self.addNodeService(node=host.name, service=quaggaSvc,
                                nodeConfig=quaggaSvcConfig)

            # Attach the quaggaContainer to the IXP Fabric Switch

           # self.addLink(quaggaContainer, ixpfabric)'''


'''
def cs123net():
	topo = QuaggaTopo()
	net = Mininet(topo = topo) #, controller=RemoteController)
	net.start()

	h1, h2, r1, r2, r3, r4 = net.get('host1', 'host2', 'router1', 'router2', 'router3', 'router4')

	h1intf = h1.defaultIntf()
	h1intf.setIP('192.168.1.1/24')

	
	h2intf = h2.defaultIntf()
	h2intf.setIP('192.168.2.1/24')
'''
