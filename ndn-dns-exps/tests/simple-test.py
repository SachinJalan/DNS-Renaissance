from subprocess import PIPE
from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.util import MiniNDNCLI, getPopen, copyExistentFile
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.experiment import Experiment
from time import sleep
from collections import defaultdict
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from traffic.query_gen import DnsTrafficGenerator
import csv
import signal
import shutil
from mininet.topo import Topo
import glob


def run():
    Minindn.cleanUp()
    Minindn.verifyDependencies()
    topo = Topo()
    info("Setup of Topology\n")
    a = topo.addHost('a')  # Receiver
    b = topo.addHost('b')  # Source for domain 1
    c = topo.addHost('c')  # Source for domain 2

    topo.addLink(a, b, delay='10ms', bw=10) # bw = bandwidth
    topo.addLink(b, c, delay='10ms', bw=10)
    topo.addLink(a, c, delay='10ms', bw=10)

    ndn = Minindn(topo=topo)
    ndn.start()

    info("Configuring NFD\n")
    AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")
    info("Configuring NLSR\n")
    AppManager(ndn, ndn.net.hosts, Nlsr, logLevel="INFO")
    
    info("Waiting for NLSR convergence...\n")
    Experiment.checkConvergence(ndn, ndn.net.hosts, convergenceTime=30)
    
    # Dictionary to store the client-side cache
    client_cache = {}  # Format: {domain+rtype: content}
    
    domains_txt = "/home/mithilpn/projects/domain.txt"
    dnsrecon_results_dir = "/home/mithilpn/projects/dns_results"
    server_conf_dir = "/home/mithilpn/projects/ndn-dns-exps/server-configs"

    if not os.path.exists(domains_txt):
        print(f"Domains file {domains_txt} not found.")
        return
    
    # Load domains and build traffic
    with open(domains_txt, "r") as file:
        domains = [line.strip() for line in file]
        domains_dict = {}
        for domain in domains[:2]:
            rtypes = []
            domain_base = domain.rstrip(".")
            csv_file = os.path.join(dnsrecon_results_dir, f"{domain_base}.csv")
            if not os.path.exists(csv_file):
                print(f"CSV file for {domain_base} not found.")
                continue
            with open(csv_file) as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    rtype = row[1]
                    if rtype not in rtypes:
                        rtypes.append(rtype)
            domains_dict[domain_base] = rtypes

    # Generate traffic requests
    generator = DnsTrafficGenerator(domains_dict, ['a',], alpha=1.0, rate=1.0)
    traffic = generator.generate_traffic(n_requests=5, n_warmup_requests=0)
    domain_keys = list(domains_dict.keys())
    sources = ["b", "c"]
    
    # === STEP 1: Start traffic servers on sources ===
    for i, source in enumerate(sources):
        domain = domain_keys[i]
        conf_path = os.path.join(server_conf_dir, f"{domain}.-server.conf")
        
        # Verify config file exists
        if not os.path.exists(conf_path):
            info(f"ERROR: Config file {conf_path} not found!\n")
            continue
        
        # Create server config directory
        ndn.net[source].cmd("mkdir -p server-config")
        
        # Create content and correctly format server config file
        info(f"Creating traffic server config for {domain} on {source}\n")
        if domain == "google.com":
            config_content = "Name=/com/google\nFreshnessPeriod=1000\nContent={\"dns\":\"google.com\",\"records\":[{\"type\":\"A\",\"value\":\"142.250.182.174\"},{\"type\":\"AAAA\",\"value\":\"2404:6800:4002:82e::200e\"}]}"
        else:  # googleapis.com
            config_content = "Name=/com/googleapis\nFreshnessPeriod=1000\nContent={\"dns\":\"googleapis.com\",\"records\":[{\"type\":\"A\",\"value\":\"142.250.194.228\"},{\"type\":\"AAAA\",\"value\":\"2404:6800:4009:828::2004\"}]}"
        
        # Write config directly to node
        config_path = f"{ndn.workDir}/{source}/server-config/{domain}-server.conf"
        ndn.net[source].cmd(f'echo "{config_content}" > server-config/{domain}-server.conf')
        
        # Start traffic server with debugging
        info(f"Starting traffic server for {domain} on {source}\n")
        out = ndn.net[source].cmd(
            f"ndn-traffic-server server-config/{domain}-server.conf > server-log.txt 2>&1 &"
        )
        
        # Prepare NDN prefix with correct format
        prefix = "/" + "/".join(domain.split(".")[::-1])
        info(f"Advertising {prefix} on {source}\n")
        
        # Advertise with NLSR and create direct route setup
        ndn.net[source].cmd(f'nlsrc advertise {prefix}')
        
        # Use direct route setup with Nfdc to ensure connectivity
        for host in ndn.net.hosts:
            if host.name != source:
                info(f"Creating direct route from {host.name} to {source} for {prefix}\n")
                host_links = host.connectionsTo(ndn.net[source])
                if host_links:
                    interface = host_links[0][0]
                    source_ip = host_links[0][1].IP()
                    Nfdc.createFace(host, source_ip)
                    Nfdc.registerRoute(host, prefix, source_ip, cost=0)
                    Nfdc.setStrategy(host, prefix, Nfdc.STRATEGY_BEST_ROUTE)
                    
        # Verify that the config was created correctly
        info(f"Config file on {source}:\n{ndn.net[source].cmd('cat server-config/' + domain + '-server.conf')}\n")
        
        # Wait a moment for the server to start up
        sleep(1)
        
        # Verify server is running
        server_pid = ndn.net[source].cmd("pgrep -f ndn-traffic-server")
        if server_pid:
            info(f"Traffic server running on {source} with PID {server_pid}\n")
        else:
            info(f"WARNING: Traffic server not running on {source}!\n")
            
            # Attempt to start with more debugging
            debug_output = ndn.net[source].cmd(f"ndn-traffic-server server-config/{domain}-server.conf")
            info(f"Debug output from server startup attempt: {debug_output}\n")
    
    # Let NLSR propagate routes
    info("Waiting for routes to propagate...\n")
    sleep(10)
    
    # Show FIB state on each host to confirm routes
    for host in ndn.net.hosts:
        info(f"Routes in {host.name}'s FIB:\n")
        info(host.cmd(f"nfdc fib list | grep -E '/com/(google|googleapis)'"))
    
    # === STEP 2: Perform ndnpeek requests ===
    info("Starting DNS lookup requests...\n")
    
    # Create directory for peek results
    consumer = ndn.net['a']
    consumer.cmd("mkdir -p peek-data")
    
    # Setup circular buffer cache with fixed size
    CACHE_SIZE = 5
    cache_keys = [""] * CACHE_SIZE
    cache_values = [""] * CACHE_SIZE
    cache_index = 0
    cache_map = {}
    
    # Process each DNS request
    for event in traffic:
        receiver = event["reciever"]
        domain = event["domain"]
        rtype = event["rtype"]
        content_name = f"{'/'.join(domain.split('.')[-1::-1])}"
        timestamp = event["timestamp"]
        
        # Create unique cache key
        cache_key = f"{domain}:{rtype}"
        
        # Check cache
        if cache_key in cache_map:
            position = cache_map[cache_key]
            cached_value = cache_values[position]
            info(f"CACHE HIT: Using cached result for {domain} {rtype}\n")
            info(f"Cached content: {cached_value}\n")
            continue
        
        # Not in cache, perform ndnpeek (without unsupported -t option)
        info(f"CACHE MISS: Requesting {domain} {rtype} via {content_name}\n")
        
        # Run ndnpeek - use basic syntax without timeout
        peek_output = consumer.cmd(f"ndnpeek -p {content_name}")
        
        # Save output to file and log
        consumer.cmd(f"echo '{peek_output}' > peek-data/{domain}-{rtype}.txt")
        info(f"ndnpeek output: {peek_output}\n")
        
        # Check for errors in the output
        if "ERROR" in peek_output:
            info(f"Warning: ndnpeek returned an error: {peek_output}\n")
            # Try with different flag format in case syntax is different
            peek_output = consumer.cmd(f"ndnpeek {content_name}")
            info(f"Retry with basic syntax: {peek_output}\n")
            consumer.cmd(f"echo '{peek_output}' >> peek-data/{domain}-{rtype}.txt")
        
        # Store in cache
        if peek_output and ("ERROR" not in peek_output):
            # If existing key at position, remove from map
            if cache_keys[cache_index] in cache_map:
                del cache_map[cache_keys[cache_index]]
            
            cache_keys[cache_index] = cache_key
            cache_values[cache_index] = peek_output
            cache_map[cache_key] = cache_index
            cache_index = (cache_index + 1) % CACHE_SIZE
            
            info(f"Stored result in cache for {domain} {rtype} at position {(cache_index-1) % CACHE_SIZE}\n")
    
    # Show ping server log to see if any requests were received
    info("\nTraffic Server Logs:\n")
    for source in sources:
        info(f"=== {source} Server Log ===\n")
        info(ndn.net[source].cmd("cat server-log.txt"))
    
    # === STEP 3: Show final peek results ===
    info("\nFinal Cache Contents:\n")
    for i in range(CACHE_SIZE):
        if cache_keys[i]:  # Only show non-empty cache entries
            info(f"Position {i}: {cache_keys[i]} -> {cache_values[i]}\n")
    
    info("\nPeek Results from Files:\n")
    all_results = consumer.cmd("cat peek-data/*")
    info(all_results)
    
    # Cleanup
    ndn.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run()