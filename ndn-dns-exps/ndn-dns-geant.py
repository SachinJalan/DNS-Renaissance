from subprocess import PIPE
from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.util import MiniNDNCLI, getPopen, copyExistentFile
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from time import sleep
from collections import defaultdict
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from traffic.query_gen import DnsTrafficGenerator
from minindn.helpers.experiment import Experiment
import csv
import shutil
import matplotlib as mpl
import matplotlib.pyplot as plt
# import pandas as pd

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

def start_traffic_server(ndn, domain, node, server_conf_file, iter):
        # Create server config directory
        info(f"Creating server config directory on {node}\n")
        info(ndn.net[node].cmd("mkdir -p server-config"))
        
        # Create content and correctly format server config file
        info(f"Creating traffic server config for {domain} on {node}\n")
        
        # Write config directly to node
        config_path_src = server_conf_file
        if not os.path.exists(config_path_src):
            info(f"ERROR: Config file {config_path_src} not found!\n")
            return -1
        
        config_path_dst = f"{ndn.workDir}/{node}/server-config/{domain}-server-{iter}.conf"
        shutil.copy(config_path_src, config_path_dst)
        
        # Start traffic server with debugging
        info(f"Starting traffic server for {domain} on {node}\n")
        ndn.net[node].cmd(
            f"ndn-traffic-server server-config/{domain}-server-{iter}.conf > server-log.txt 2>&1 &"
        )

        prefix = "/".join(domain.split(".")[::-1])
        print(f"Advertising prefix {prefix} on {node}\n")
        info(ndn.net[node].cmd(f'nlsrc advertise {prefix}'))
        sleep(10)  # Allow time for routing convergence
        # route_check = ndn.net[node].cmd(f'nfdc route list | grep {prefix}')
        # info(f"Route check on {node}: {route_check}\n")
 
        server_pid = ndn.net[node].cmd("pgrep -f ndn-traffic-server")
        if server_pid:
            info(f"Traffic server running on {node} with PID {server_pid}\n")
            return 0
        else:
            info(f"WARNING: Traffic server not running on {node}!\n")
            return -1

def run_dns_ndn_experiments(n_requests=10, n_warmup_requests=0, alpha=1.0, rate=1.0):
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

    # print("Receivers:", receivers, len(receivers))
    # print("ICR Candidates:", icr_candidates, len(icr_candidates))
    # print("Source Attachments:", source_attachments, len(source_attachments))
    # print("Sources:", sources, len(sources))

    ndn = Minindn(topo=topology)
    ndn.start()

    # Start NFD and NLSR on nodes
    info("Configuring NFD\n")
    # Configure NFD with different cache sizes for different node types csSize=100000, csPolicy="lru", csUnsolicitedPolicy="drop-all")
    AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")
    info("Configuring NLSR\n")
    AppManager(ndn, ndn.net.hosts, Nlsr, logLevel="DEBUG")
    info("Waiting for NLSR convergence...\n")
    Experiment.checkConvergence(ndn, ndn.net.hosts, convergenceTime=90)
    domains_txt = "/home/mithilpn/projects/domain.txt"
    dnsrecon_results_dir = "/home/mithilpn/projects/dns_results"
    server_conf_dir = "/home/mithilpn/projects/ndn-dns-exps/ndn-server-configs"
    if not os.path.exists(domains_txt):
        print(f"Domains file {domains_txt} not found.")
        return
    
    with open(domains_txt, "r") as file:
        domains = [line.strip() for line in file]
        domains_dict = {}
        for domain in domains:
            rtypes = []
            csv_file = os.path.join(dnsrecon_results_dir, f"{domain}.csv")
            if  domain[-1] != ".":
                domain += "."
            if not os.path.exists(csv_file):
                print(f"CSV file for {domain} not found.")
                continue
            with open(csv_file) as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    rtype = row[1]
                    if rtype not in rtypes:
                        rtypes.append(rtype)
            domains_dict[domain] = rtypes

    total_requests = n_requests + n_warmup_requests
    generator = DnsTrafficGenerator(domains_dict, receivers, alpha=alpha, rate=rate)
    traffic = generator.generate_traffic(n_requests=n_requests, n_warmup_requests=n_warmup_requests)
    domains = list(domains_dict.keys())
    total_time = 0
    domain_source_map = {}

    assert len(domains) == len(sources), "Number of sources and domains do not match."

    # allot sources to domains
    for i in range(len(sources)):
        source = sources[i]
        domain = domains[i]
        domain_source_map[domain] = source

    # Start traffic servers on sources
    for i, domain in enumerate(domains):
        source = domain_source_map[domain]
        server_conf_file = f"{server_conf_dir}/{domain}-server.conf"
        info(f"Starting traffic server for {domain} on {source}\n")
        result = start_traffic_server(ndn, domain, source, server_conf_file, 0)
        if result != 0:
            info(f"Failed to start traffic server for {domain} on {source}\n")
            return

    info("Starting DNS lookup requests...\n")

    # CACHE_SIZE = 0
    # caches = {}
    # wrtie_indexs = {}
    for receiver in receivers:
        # caches[receiver] = [[],] * CACHE_SIZE
        # wrtie_indexs[receiver] = 0
        if not os.path.exists(f"{ndn.workDir}/{receiver}/client-log.txt"):
            with open(f"{ndn.workDir}/{receiver}/client-log.txt", "w") as f:
                f.write("Client log file\n")
    
    for i, event in enumerate(traffic):
        receiver = event["receiver"]
        domain = event["domain"]
        rtype = event["rtype"]
        base_prefix = "/".join(domain.split(".")[::-1])
        content_name = f"{base_prefix}/{rtype}" 
        timestamp = event["timestamp"]
        if event["log"]:
            log = 1
        else:
            log = 0

        # cache = caches[receiver]
        # wrtie_index = wrtie_indexs[receiver]

        # Check cache
        # for cache_entry in cache:
        #     if cache_entry and cache_entry[0] == domain.rstrip(".") and cache_entry[1] == rtype:
        #         info(f"CACHE HIT: Using cached result for {domain} {rtype}\n")
        #         info(f"Cached content: {cache_entry}\n")
        #         total_time += 0*log
        #         continue

        consumer = ndn.net[receiver]
        # info(f"CACHE MISS: {receiver} Requesting {domain} {rtype} via {content_name}\n")

        ndnpeek_cmd = f"ndnpeek -p {content_name} -v"
        peek_output = consumer.cmd(ndnpeek_cmd)
        info(f"ndnpeek output\n: {peek_output}\n##########################\n")

        with open(f"{ndn.workDir}/{receiver}/client-log.txt", "a") as f:
            f.write(f"Domain: {domain}, Rtype: {rtype}, Output: {peek_output}\n")

        # Extract RTT info from peek_output
        rtt = peek_output.split("RTT: ")[1].split("ms")[0]
        if rtt:
            total_time += float(rtt)*log
            info(f"RTT for {domain} {rtype}: {rtt} ms\n")


        
        # get the peek output file from the consumer a
        # consumer.cmd(f"mv peek-data/{domain}-{rtype}.txt {ndn.workDir}/{consumer.name}/peek-data/")

        
        # Check for errors in the output string
        if "ERROR" in peek_output or "Nack" in peek_output or "NoRoute" in peek_output:
             info(f"Warning: ndnpeek returned an error or Nack/NoRoute: {peek_output}\n")

        # Store in cache (only if successful - check for common failure indicators)
        # if peek_output and "ERROR" not in peek_output and "Nack" not in peek_output and "NoRoute" not in peek_output:
        #     # parse peek_output to get the content
        #     records = [unparsed_rec.split("-") for unparsed_rec in peek_output.split("+")]
        #     for record in records:
        #         cache[wrtie_index] = record
        #         # info(f"Stored result in cache for {record[0]} {record[1]} at position {wrtie_index}\n")
        #         wrtie_index = (wrtie_index + 1) % CACHE_SIZE
            
        # caches[receiver] = cache
        # wrtie_indexs[receiver] = wrtie_index
    
    print(f"########################################\nTotal time taken for all requests: {total_time} ms\n")
    print(f"Average time taken for all requests: {total_time / n_requests} ms\n")
    ndn.stop()
    return total_time / n_requests

def run_dns_hierarchical_experiment(n_requests=10, n_warmup_requests=0, alpha=1.0, rate=1.0):
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

    # print("Receivers:", receivers, len(receivers))
    # print("ICR Candidates:", icr_candidates, len(icr_candidates))
    # print("Source Attachments:", source_attachments, len(source_attachments))
    # print("Sources:", sources, len(sources))

    ndn = Minindn(topo=topology)
    ndn.start()

    # Start NFD and NLSR on nodes
    info("Configuring NFD\n")
    # Configure NFD with different cache sizes for different node types csSize=100000, csPolicy="lru", csUnsolicitedPolicy="drop-all")
    AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG", csSize=0, csUnsolicitedPolicy="drop-all")
    info("Configuring NLSR\n")
    AppManager(ndn, ndn.net.hosts, Nlsr, logLevel="DEBUG")
    info("Waiting for NLSR convergence...\n")
    Experiment.checkConvergence(ndn, ndn.net.hosts, convergenceTime=90)
    domains_txt = "/home/mithilpn/projects/domain.txt"
    dnsrecon_results_dir = "/home/mithilpn/projects/dns_results"
    server_conf_dir = "/home/mithilpn/projects/ndn-dns-exps/dns-server-configs"
    if not os.path.exists(domains_txt):
        print(f"Domains file {domains_txt} not found.")
        return
    
    with open(domains_txt, "r") as file:
        domains = [line.strip() for line in file]
        domains_dict = {}
        for domain in domains:
            rtypes = []
            csv_file = os.path.join(dnsrecon_results_dir, f"{domain}.csv")
            if  domain[-1] != ".":
                domain += "."
            if not os.path.exists(csv_file):
                print(f"CSV file for {domain} not found.")
                continue
            with open(csv_file) as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    rtype = row[1]
                    if rtype not in rtypes:
                        rtypes.append(rtype)
            domains_dict[domain] = rtypes

    total_requests = n_requests + n_warmup_requests
    generator = DnsTrafficGenerator(domains_dict, receivers, alpha=1.0, rate=1.0)
    traffic = generator.generate_traffic(n_requests=n_requests, n_warmup_requests=n_warmup_requests)
    domains = list(domains_dict.keys())
    total_time = 0
    domain_source_map = {}

    assert len(domains) == len(sources), "Number of sources and domains do not match."

    # allot sources to domains
    for i in range(len(sources)):
        source = sources[i]
        domain = domains[i]
        domain_source_map[domain] = source

    # Start traffic servers on sources
    for i, domain in enumerate(domains):
        source = domain_source_map[domain]
        server_conf_file = f"{server_conf_dir}/{domain}-server.conf"
        info(f"Starting traffic server for {domain} on {source}\n")
        result = start_traffic_server(ndn, domain, source, server_conf_file, 0)
        if result != 0:
            info(f"Failed to start traffic server for {domain} on {source}\n")
            return

    info("Starting DNS lookup requests...\n")


    for receiver in receivers:
        if not os.path.exists(f"{ndn.workDir}/{receiver}/client-log.txt"):
            with open(f"{ndn.workDir}/{receiver}/client-log.txt", "w") as f:
                f.write("Client log file\n")
    
    for i, event in enumerate(traffic):
        receiver = event["receiver"]
        domain = event["domain"]
        rtype = event["rtype"]
        base_prefix = "/".join(domain.split(".")[::-1])
        content_name = f"{base_prefix}/{rtype}" 
        timestamp = event["timestamp"]
        if event["log"]:
            log = 1
        else:
            log = 0

        consumer = ndn.net[receiver]

        ndnpeek_cmd = f"ndnpeek -p {content_name} -v"
        peek_output = consumer.cmd(ndnpeek_cmd)
        info(f"ndnpeek output\n: {peek_output}\n##########################\n")

        with open(f"{ndn.workDir}/{receiver}/client-log.txt", "a") as f:
            f.write(f"Domain: {domain}, Rtype: {rtype}, Output: {peek_output}\n")

        # Extract RTT info from peek_output
        rtt = peek_output.split("RTT: ")[1].split("ms")[0]
        if rtt:
            total_time += float(rtt)*log*3
            info(f"RTT for {domain} {rtype}: {rtt} ms\n")

        if "ERROR" in peek_output or "Nack" in peek_output or "NoRoute" in peek_output:
             info(f"Warning: ndnpeek returned an error or Nack/NoRoute: {peek_output}\n")

    print(f"########################################\nTotal time taken for all requests: {total_time} ms\n")
    print(f"Average time taken for all requests: {total_time / n_requests} ms\n")
    ndn.stop()
    return total_time / n_requests

def plot_comparison(alphas, ndn_times, dns_times, output_path="resolution_times_comparison.png"):
    """
    Create a line plot comparing NDN and hierarchical DNS resolution times for different alpha values.
    
    Args:
        alphas: List of alpha values used in the experiments
        ndn_times: List of average resolution times for NDN
        dns_times: List of average resolution times for hierarchical DNS
        output_path: Path to save the plot
    """
    plt.figure(figsize=(12, 8))
    
    # Set font properties
    mpl.rcParams["font.family"] = "Open Sans"
    mpl.rcParams["font.size"] = 20
    
    # Create the line plot
    plt.plot(alphas, ndn_times, 'o-', linewidth=3, markersize=10, label='NDN-DNS')
    plt.plot(alphas, dns_times, 's-', linewidth=3, markersize=10, label='Hierarchical DNS')
    
    # Add labels and title
    plt.xlabel('Zipf Alpha Parameter')
    plt.ylabel('Average Resolution Time (ms)')
    plt.title('DNS Resolution Time Comparison')
    
    # Add grid and legend
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='best', fontsize=18)
    
    # Set y-axis to start from 0
    plt.ylim(bottom=0)
    
    # Adjust margins and layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    setLogLevel('info')
    alphas = [0.25, 1.0, 2]
    ndn_dns_exp_runs_results = []
    for alpha in alphas:
        res = run_dns_ndn_experiments(n_requests=100, n_warmup_requests=10, alpha=alpha)
        ndn_dns_exp_runs_results.append(res)
    print(">>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<")
    print(ndn_dns_exp_runs_results)

    dns_exp_runs_results = []
    for alpha in alphas:
        res = run_dns_hierarchical_experiment(n_requests=100, n_warmup_requests=0, alpha=alpha)
        dns_exp_runs_results.append(res)
    print(">>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<")
    print(dns_exp_runs_results)

    # Create the comparison plot
    plot_comparison(
        alphas=alphas,
        ndn_times=ndn_dns_exp_runs_results,
        dns_times=dns_exp_runs_results,
        output_path="/home/mithilpn/projects/ndn-dns-exps/resolution_times_comparison.png"
    )
    

