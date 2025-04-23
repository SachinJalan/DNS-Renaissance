from subprocess import PIPE
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.link import TCLink
from collections import defaultdict
import time
import os, sys
import shutil
import csv
import re
import subprocess
import random
from datetime import datetime

class GeantTopo(Topo):
    """
    Create a topology based on the GEANT network.
    """
    def build(self, topo_path):
        # Process topology file
        with open(topo_path, 'r') as f:
            lines = f.readlines()
        
        # Parse nodes
        nodes = {}
        links = []
        parsing_nodes = False
        parsing_links = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('[nodes]'):
                parsing_nodes = True
                parsing_links = False
                continue
            elif line.startswith('[links]'):
                parsing_nodes = False
                parsing_links = True
                continue
            
            if parsing_nodes and line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 1:
                    node_name = parts[0]
                    nodes[node_name] = self.addHost(node_name)
            
            if parsing_links and line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 3:
                    node1, node2 = parts[0], parts[1]
                    delay = parts[2] if len(parts) > 2 else '10ms'
                    bw = float(parts[3]) if len(parts) > 3 else 10
                    links.append((node1, node2, delay, bw))
        
        # Add links
        for node1, node2, delay, bw in links:
            if node1 in nodes and node2 in nodes:
                self.addLink(nodes[node1], nodes[node2], delay=delay, bw=bw)

def classify_hosts(topology):
    """
    Classify hosts into receivers, candidates for TLD/root, and source attachments based on their degree.
    """
    deg = defaultdict(int)
    for link in topology.links():
        node1, node2 = link
        deg[node1] += 1
        deg[node2] += 1

    receivers = [v for v in topology.nodes() if deg[v] == 1]
    server_candidates = [v for v in topology.nodes() if deg[v] > 2]
    source_attachments = [v for v in topology.nodes() if deg[v] == 2]

    # Sort server candidates by degree for better selection
    server_candidates.sort(key=lambda x: deg[x], reverse=True)

    return {
        "receivers": receivers,
        "server_candidates": server_candidates,
        "source_attachments": source_attachments,
    }

def cleanup():
    """
    Clean up the Mininet environment.
    """
    info("Stopping DNS servers and cleaning up...\n")
    subprocess.run(['sudo', 'pkill', '-f', 'named'])
    subprocess.run(['sudo', 'mn', '-c'])
    info("Mininet stopped. Cleaning up temporary files...\n")
    if os.path.exists('/tmp/dns-server-confs'):
        shutil.rmtree('/tmp/dns-server-confs')

def setup_dns_server(net, node_name, config_file, server_type="authoritative"):
    """
    Set up a DNS server on a node.
    """
    node = net.getNodeByName(node_name)
    
    # Create server config directory
    info(f"Creating DNS server configuration for {node_name} ({server_type})\n")
    
    # Create directories for DNS server
    node.cmd('mkdir -p /var/named')
    node.cmd('mkdir -p /etc/bind')
    
    # Copy config file to the node
    if not os.path.exists(config_file):
        info(f"ERROR: Config file {config_file} not found!\n")
        return False
    
    node.cmd(f'cp {config_file} /etc/bind/named.conf')
    
    # If there are zone files, copy them too
    zone_dir = os.path.dirname(config_file) + '/zones/'
    if os.path.exists(zone_dir):
        for zone_file in os.listdir(zone_dir):
            node.cmd(f'cp {zone_dir}/{zone_file} /var/named/')
    
    # Start BIND DNS server
    info(f"Starting DNS server on {node_name}\n")
    output = node.cmd('named -g > dns_server.log 2>&1 &')
    
    # Verify that the server is running
    time.sleep(2)  # Give the server some time to start
    pid = node.cmd('pgrep named')
    if pid:
        info(f"DNS server running on {node_name} with PID {pid}\n")
        return True
    else:
        info(f"WARNING: DNS server failed to start on {node_name}!\n")
        info(f"Error output: {output}\n")
        return False

def run_dns_query(net, client, domain, dns_server):
    """
    Run a DNS query and measure response time.
    """
    # Use dig with +stats to get query time
    cmd = f'dig @{dns_server} {domain} +norecurse +tries=1 +time=10 +stats'
    start_time = time.time()
    output = client.cmd(cmd)
    
    # Extract query time from dig output
    match = re.search(r'Query time: (\d+) msec', output)
    if match:
        query_time = int(match.group(1))
    else:
        # If dig doesn't report query time, calculate it manually
        query_time = int((time.time() - start_time) * 1000)
        
    return {
        'output': output,
        'query_time': query_time,
        'success': 'ANSWER SECTION' in output
    }

def run(n_requests=10, n_warmup_requests=0):
    """
    Run the hierarchical DNS experiment.
    """
    # Cleanup any previous run
    cleanup()
    
    # Process topology
    geant_topo_path = "/home/mithilpn/projects/mini-ndn/topologies/geant.conf"
    topo = GeantTopo(topo_path=geant_topo_path)
    
    # Create Mininet network
    net = Mininet(topo=topo, controller=Controller, switch=OVSSwitch, link=TCLink)
    net.start()
    
    # Classify hosts
    host_classification = classify_hosts(topo)
    receivers = host_classification["receivers"]
    server_candidates = host_classification["server_candidates"]
    source_attachments = host_classification["source_attachments"]
    
    # Select nodes for root and TLD servers
    root_server = server_candidates[0]
    tld_servers = {}  # Will map TLDs to server nodes
    
    # Load domain data
    domains_txt = "/home/mithilpn/projects/domain.txt"
    dnsrecon_results_dir = "/home/mithilpn/projects/dns_results"
    dns_conf_dir = "/home/mithilpn/projects/dns-configs"  # Directory with DNS server configs
    
    if not os.path.exists(domains_txt):
        print(f"Domains file {domains_txt} not found.")
        net.stop()
        return
    
    with open(domains_txt, "r") as file:
        domains = [line.strip() for line in file]
        domains_dict = {}
        
        # Group domains by TLD
        tld_domains = defaultdict(list)
        
        for domain in domains:
            rtypes = []
            if domain[-1] != ".":
                domain += "."
                
            # Extract TLD
            parts = domain.split('.')
            if len(parts) >= 3:  # Ensure we have at least one label plus TLD
                tld = parts[-2]  # Second-to-last part (before the trailing dot)
                tld_domains[tld].append(domain)
            
            csv_file = os.path.join(dnsrecon_results_dir, f"{domain.rstrip('.')}.csv")
            if not os.path.exists(csv_file):
                print(f"CSV file for {domain} not found.")
                continue
                
            with open(csv_file) as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for row in reader:
                    rtype = row[1]
                    if rtype not in rtypes:
                        rtypes.append(rtype)
            
            domains_dict[domain] = rtypes
    
    # Assign TLD servers - one per TLD if possible
    tld_list = list(tld_domains.keys())
    server_idx = 1  # Start from 1 as 0 is used for root
    
    for tld in tld_list:
        if server_idx < len(server_candidates):
            tld_servers[tld] = server_candidates[server_idx]
            server_idx += 1
        else:
            # Reuse servers if we have more TLDs than candidates
            tld_servers[tld] = server_candidates[1 + (server_idx % (len(server_candidates)-1))]
            server_idx += 1
    
    # Assign authoritative servers
    auth_servers = {}
    remaining_candidates = [c for c in server_candidates if c != root_server and c not in tld_servers.values()]
    
    for i, domain in enumerate(domains):
        # Assign from source_attachments or recycle through remaining candidates
        if i < len(source_attachments):
            auth_servers[domain] = source_attachments[i]
        else:
            idx = i % len(remaining_candidates) if remaining_candidates else i % len(source_attachments)
            auth_servers[domain] = (remaining_candidates if remaining_candidates else source_attachments)[idx]
    
    print("Receivers:", receivers, len(receivers))
    print("Root Server:", root_server)
    print("TLD Servers:", tld_servers)
    print("Authoritative Servers:", auth_servers)
    
    # Set up DNS servers
    # Root server configuration
    root_config = f"{dns_conf_dir}/root/named.conf"
    if not setup_dns_server(net, root_server, root_config, "root"):
        print(f"Failed to set up root server on {root_server}")
        net.stop()
        return
    
    # TLD servers configuration
    for tld, server in tld_servers.items():
        tld_config = f"{dns_conf_dir}/tld/{tld}/named.conf"
        if not setup_dns_server(net, server, tld_config, f"TLD .{tld}"):
            print(f"Failed to set up TLD server for .{tld} on {server}")
            net.stop()
            return
    
    # Authoritative servers configuration
    for domain, server in auth_servers.items():
        auth_config = f"{dns_conf_dir}/auth/{domain.rstrip('.')}/named.conf"
        if not setup_dns_server(net, server, auth_config, f"authoritative for {domain}"):
            print(f"Failed to set up authoritative server for {domain} on {server}")
            net.stop()
            return
    
    # Configure clients to use the root server
    for receiver in receivers:
        client = net.getNodeByName(receiver)
        # Create resolv.conf pointing to the root server
        client.cmd(f'echo "nameserver {net.getNodeByName(root_server).IP()}" > /etc/resolv.conf')
    
    # Generate DNS queries based on the traffic pattern
    total_requests = n_requests + n_warmup_requests
    queries = []
    
    # Similar traffic generation as in NDN script
    for i in range(total_requests):
        domain = random.choice(list(domains_dict.keys()))
        rtype = random.choice(domains_dict[domain])
        receiver = random.choice(receivers)
        queries.append({
            'receiver': receiver,
            'domain': domain,
            'rtype': rtype,
            'timestamp': datetime.now().timestamp(),
            'is_warmup': i < n_warmup_requests
        })
    
    # Run queries and measure times
    info("Starting DNS lookup requests...\n")
    query_times = []
    
    for i, query in enumerate(queries):
        receiver = query['receiver']
        domain = query['domain']
        rtype = query['rtype']
        is_warmup = query['is_warmup']
        
        client = net.getNodeByName(receiver)
        
        info(f"{'WARMUP: ' if is_warmup else ''}Client {receiver} querying for {domain} {rtype}\n")
        
        # Run query using the root server
        result = run_dns_query(net, client, domain, net.getNodeByName(root_server).IP())
        
        if result['success']:
            info(f"Query successful, took {result['query_time']} ms\n")
            if not is_warmup:
                query_times.append(result['query_time'])
        else:
            info(f"Query failed: {result['output']}\n")
        
        # Add a small delay between queries
        time.sleep(0.5)
    
    # Calculate statistics
    if query_times:
        avg_time = sum(query_times) / len(query_times)
        print(f"########################################")
        print(f"Total time taken for all requests: {sum(query_times)} ms")
        print(f"Average time taken for all requests: {avg_time} ms")
        print(f"Number of successful queries: {len(query_times)}")
    else:
        print("No successful queries recorded.")
    
    net.stop()
    cleanup()

if __name__ == "__main__":
    setLogLevel('info')
    run()
