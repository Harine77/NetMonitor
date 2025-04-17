from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import RemoteController

class CustomTopology(Topo):
    def build(self):
        switch = self.addSwitch('s1')
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')

        # Adding links with bandwidth limits
        self.addLink(host1, switch, bw=100)  # 100 Mbps
        self.addLink(host2, switch, bw=100)

if __name__ == '__main__':
    net = Mininet(topo=CustomTopology(), link=TCLink, controller=RemoteController)
    
    net.start()
    CLI(net)  # Start Mininet CLI for debugging
    net.stop()
