from subprocess import PIPE
from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.util import MiniNDNCLI, getPopen, copyExistentFile
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from time import sleep
from collections import defaultdict
from query_gen import DnsTrafficGenerator
import os
import signal

def classify_hosts(topology):
    """
    Classify hosts into receivers, ICR candidates, and source attachments based on their degree.
    """
    deg = defaultdict(int)
    for link in topology.links():
        node1, node2 = link
        deg[node1] += 1
        deg[node2] += 1

    receivers = [v for v in topology.nodes() if deg[v] == 1]
    icr_candidates = [v for v in topology.nodes() if deg[v] > 2]
    source_attachments = [v for v in topology.nodes() if deg[v] == 2]

    return {
        "receivers": receivers,
        "icr_candidates": icr_candidates,
        "source_attachments": source_attachments,
    }

def create_server_conf(source, prefix, conf_dir):
    """
    Create a configuration file for an NDN traffic server.
    """
    conf_path = os.path.join(conf_dir, f"{source}-server.conf")
    with open(conf_path, "w") as conf_file:
        conf_file.write(f"Name={prefix}\n")
        conf_file.write("Content=SampleContent\n")
        conf_file.write("FreshnessPeriod=1000\n")
        conf_file.write("ContentType=0\n")
    return conf_path

def cleanup(ndn):
    """
    Clean up the Mini-NDN environment by stopping all processes and removing temporary files.
    """
    info("Stopping NFD and NLSR on all nodes...\n")
    for host in ndn.net.hosts:
        host.cmd("killall ndn-traffic-server ndnping nfd nlsr || true")
    ndn.stop()
    info("Mini-NDN stopped. Cleaning up temporary files...\n")
    os.system("rm -rf /tmp/ndn-server-confs")

def run():
    Minindn.cleanUp()
    Minindn.verifyDependencies()
    geant_topo_path = "/home/mithilpn/projects/mini-ndn/topologies/geant.conf"
    topology, faces = Minindn.processTopo(geant_topo_path)

    # Classify hosts
    host_classification = classify_hosts(topology)
    receivers = host_classification["receivers"]
    icr_candidates = host_classification["icr_candidates"]
    source_attachments = host_classification["source_attachments"]

    # Add sources to the topology
    sources = []
    for v in source_attachments:
        u = f"source-{v}"
        topology.addHost(u)
        topology.addLink(v, u, delay='10ms', bw=10)
        sources.append(u)

    print("Receivers:", receivers, len(receivers))
    print("ICR Candidates:", icr_candidates, len(icr_candidates))
    print("Source Attachments:", source_attachments, len(source_attachments))
    print("Sources:", sources, len(sources))

    ndn = Minindn(topo=topology)
    ndn.start()

    # Start NFD and NLSR on nodes
    info('Starting NFD on nodes...\n')
    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nfds.start()
    info('Starting NLSR on nodes...\n')
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
    nlsrs.start()
    sleep(10)  # Allow time for NLSR to converge

    # Create and start traffic servers for sources
    conf_dir = "/home/mithilpn/projects/ndn-dns-exps/ndn-server-confs"
    os.makedirs(conf_dir, exist_ok=True)
    domains = {f"domain{i}": ["A", "AAAA", "CNAME"] for i in range(1, 16)}
    domain_names = list(domains.keys())
    for i in range(len(sources)):
        source = sources[i]
        domain = domain_names[i]
        prefix = f"/com/{domain}"
        conf_path = create_server_conf(source, prefix, conf_dir)
        ndn.net[source].cmd(f"ndn-traffic-server {conf_path} &")

    generator = DnsTrafficGenerator(domains, receivers, alpha=1.2, rate=5.0)
    traffic = generator.generate_traffic(n_requests=10, n_warmup_requests=0)

    for event in traffic:
        receiver = event["reciever"]
        domain = event["domain"]
        rtype = event["rtype"]
        prefix = f"/com/{domain}"
        timestamp = event["timestamp"]

        ndn.net[receiver].cmd(f"ndnping {prefix} -c 1 &")
        if event["log"]:
            info(f"Timestamp: {timestamp}, Receiver: {receiver}, Domain: {domain}, RType: {rtype}\n")

    MiniNDNCLI(ndn.net)
    cleanup(ndn)


if __name__ == "__main__":
    setLogLevel('info')
    run()