from subprocess import PIPE
from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.helpers.experiment import Experiment
from time import sleep
import os, sys, csv, shutil
from mininet.topo import Topo

# Fix cache initialization and variable typos
CACHE_SIZE = 100

class TriangleTopo(Topo):
    def build(self):
        a = self.addHost('a')  # Receiver
        b = self.addHost('b')  # Source for domain 1
        c = self.addHost('c')  # Source for domain 2
        self.addLink(a, b, delay='10ms', bw=10)
        self.addLink(b, c, delay='10ms', bw=10)
        self.addLink(a, c, delay='10ms', bw=10)


def run():
    Minindn.cleanUp()
    Minindn.verifyDependencies()
    topo = TriangleTopo()
    info("** Setting up topology...\n")

    ndn = Minindn(topo=topo)
    ndn.start()

    # Configure NFD and NLSR
    info("** Starting NFD on all nodes...\n")
    AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")
    info("** Starting NLSR on all nodes...\n")
    AppManager(ndn, ndn.net.hosts, Nlsr, logLevel="DEBUG")
    info("** Waiting for NLSR convergence...\n")
    Experiment.checkConvergence(ndn, ndn.net.hosts, convergenceTime=20)

    # Paths
    domains_file = "/home/mithilpn/projects/domain.txt"
    dns_dir     = "/home/mithilpn/projects/dns_results"
    conf_dir    = "/home/mithilpn/projects/ndn-dns-exps/server-configs"

    if not os.path.isfile(domains_file):
        info(f"ERROR: Domains file not found: {domains_file}\n")
        return

    # Load domains and resource record types
    domains = [d.strip() for d in open(domains_file) if d.strip()]
    domains_dict = {}
    for domain in domains[:2]:
        base = domain.rstrip('.')
        csv_path = os.path.join(dns_dir, f"{base}.csv")
        if not os.path.isfile(csv_path):
            info(f"WARNING: Missing CSV for {base}\n")
            continue
        types = []
        with open(csv_path) as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                    rtype = row[1]
                    if rtype not in types:
                        types.append(rtype)
            domains_dict[domain] = types

    # Generate traffic
    from traffic.query_gen import DnsTrafficGenerator
    n_requests = 10
    n_warmup  = 0
    generator = DnsTrafficGenerator(domains_dict, ['a'], alpha=1.0, rate=1.0)
    traffic   = generator.generate_traffic(n_requests, n_warmup)

    # Initialize cache as separate lists
    cache = [[] for _ in range(CACHE_SIZE)]
    write_index = 0

    # Launch a server per domain/source
    sources = ['b', 'c']
    for i, src in enumerate(sources):
        base = list(domains_dict.keys())[i]
        node = ndn.net[src]

        # Stop any existing server
        node.cmd("pkill -f ndn-traffic-server || true")
        node.cmd("rm -rf server-config && mkdir -p server-config")

        # Copy config and start server
        conf_src = os.path.join(conf_dir, f"{base}-server.conf")
        conf_dst = f"{ndn.workDir}/{src}/server-config/{base}-server.conf"
        if not os.path.isfile(conf_src):
            info(f"ERROR: Missing config {conf_src}\n")
            continue
        shutil.copy(conf_src, conf_dst)
        info(f"** Starting traffic server on {src} for /{base}\n")
        node.cmd(f"ndn-traffic-server -c {n_requests} server-config/{base}-server.conf > server-log.txt 2>&1 &")

        # Register prefix manually to ensure FIB entries
        prefix = '/' + '/'.join(reversed(base.split('.')))  # drop empty segments
        info(node.cmd(f"nfdc register {prefix} udp4://{node.IP()}"))
        sleep(5)

        # Debug routing
        routes = node.cmd(f"nfdc route list | grep {prefix}")
        info(f"Routes for {prefix} on {src}:\n{routes}\n")

    info("** Starting queries...\n")
    for event in traffic:
        receiver = event['receiver']  # fixed typo
        base     = event['domain'].rstrip('.')
        rtype    = event['rtype']
        prefix   = '/' + '/'.join(reversed(base.split('.')))
        name     = f"{prefix}/{rtype}"
        node     = ndn.net[receiver]

        # Check cache
        hit = False
        for entry in cache:
            if entry and entry[0] == base and entry[1] == rtype:
                hit = True
                info(f"CACHE HIT: {base} {rtype}\n")
                break
        if hit:
            continue

        info(f"CACHE MISS: fetching {name}\n")
        out = node.cmd(f"ndnpeek -p {name} -v")
        logdir = f"{ndn.workDir}/{receiver}/peek-data"
        os.makedirs(logdir, exist_ok=True)
        with open(f"{logdir}/log.txt", 'a') as lg:
            lg.write(f"{name} -> {out}\n")

        if any(fl in out for fl in ('ERROR', 'Nack', 'NoRoute')):
            info(f"Warning: peek error: {out}\n")
        else:
            recs = [r.split('-') for r in out.split('+')]
            for r in recs:
                cache[write_index] = r
                write_index = (write_index + 1) % CACHE_SIZE

    ndn.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
