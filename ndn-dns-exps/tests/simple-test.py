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

def make_temp_client_config(server_config, temp_config_path):
    """
    Create a temporary client configuration file based on the server configuration.
    """
    with open(server_config, "r") as f:
        lines = f.readlines()

    # Modify the lines as needed for the client config
    modified_lines = ["TrafficPercentage=100\n"]
    for line in lines:
        if line.startswith("Content="):
            # Modify the content line for the client config
            modified_line = line.replace("Content=", "ExpectedContent=")
            modified_lines.append(modified_line)
        elif line.startswith("Name="):
            modified_lines.append(line)

    with open(temp_config_path, "w") as f:
        f.writelines(modified_lines)


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
    # topo.addLink(a, c, delay='10ms', bw=10)

    ndn = Minindn(topo=topo)
    ndn.start()

    info("Configuring NFD\n")
    AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")
    info("Configuring NLSR\n")
    AppManager(ndn, ndn.net.hosts, Nlsr, logLevel="DEBUG")
    info("Waiting for NLSR convergence...\n")
    Experiment.checkConvergence(ndn, ndn.net.hosts, convergenceTime=30)
    domains_txt = "/home/mithilpn/projects/domain.txt"
    dnsrecon_results_dir = "/home/mithilpn/projects/dns_results"
    server_conf_dir = "/home/mithilpn/projects/ndn-dns-exps/server-configs"
    # domains_txt = "domain.txt"
    # dnsrecon_results_dir = "dns_results"
    # server_conf_dir = "server-configs"

    if not os.path.exists(domains_txt):
        print(f"Domains file {domains_txt} not found.")
        return
    
    # Load domains and build traffic
    with open(domains_txt, "r") as file:
        domains = [line.strip() for line in file]
        domains_dict = {}
        for domain in domains[:2]:
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

    # Generate traffic requests
    n_requests = 4
    n_warmup_requests = 0
    total_requests = n_requests + n_warmup_requests
    receivers = ["a"]
    generator = DnsTrafficGenerator(domains_dict, receivers, alpha=1.0, rate=1.0)
    traffic = generator.generate_traffic(n_requests=n_requests, n_warmup_requests=n_warmup_requests)
    domain_keys = list(domains_dict.keys())
    sources = ["b", "c"]
    total_time = 0
    source_domain_map = {}
    # === STEP 1: Start traffic servers on sources ===
    for i, source in enumerate(sources):
        domain = domain_keys[i]
        
        # Kill any existing ndn-traffic-server instances first
        # info(f"Killing any existing ndn-traffic-server instances on {source}\n")
        # info(ndn.net[source].cmd("pkill -f ndn-traffic-server || true"))
        
        # Create server config directory
        info(f"Creating server config directory on {source}\n")
        info(ndn.net[source].cmd("mkdir -p server-config"))
        
        # Create content and correctly format server config file
        info(f"Creating traffic server config for {domain} on {source}\n")
        
        # Write config directly to node
        config_path_src = os.path.join(server_conf_dir, f"{domain}-server.conf")
        if not os.path.exists(config_path_src):
            info(f"ERROR: Config file {config_path_src} not found!\n")
            continue
        
        config_path_dst = f"{ndn.workDir}/{source}/server-config/{domain}-server.conf"
        shutil.copy(config_path_src, config_path_dst)
        
        # Start traffic server with debugging
        info(f"Starting traffic server for {domain} on {source}\n")
        ndn.net[source].cmd(
            f"ndn-traffic-server -c 1 server-config/{domain}-server.conf > server-log.txt 2>&1 &"
        )

        prefix = "/".join(domain.split(".")[::-1])
        print(f"Advertising prefix {prefix} on {source}\n")
        info(ndn.net[source].cmd(f'nlsrc advertise {prefix}'))
        sleep(10)  # Allow time for routing convergence
        route_check = ndn.net[source].cmd(f'nfdc route list | grep {prefix}')
        info(f"Route check on {source}: {route_check}\n")

        source_domain_map[source] = domain
        # Verify that the config was created correctly
        # info(f"Config file on {source}:\n{ndn.net[source].cmd('cat server-config/' + domain + '-server.conf')}\n")
    
        
        # Verify server is running
        server_pid = ndn.net[source].cmd("pgrep -f ndn-traffic-server")
        if server_pid:
            info(f"Traffic server running on {source} with PID {server_pid}\n")
        else:
            info(f"WARNING: Traffic server not running on {source}!\n")
            
            # Attempt to start with more debugging
            # debug_output = ndn.net[source].cmd(f"ndn-traffic-server -c {total_requests} server-config/{domain}-server.conf &")
            # info(f"Debug output from server startup attempt: {debug_output}\n")
    
    # Let NLSR propagate routes

    # info("Waiting for routes to propagate...\n")

    
    # Show FIB state on each host to confirm routes
    for receiver in receivers:
        info(f"Routes in {receiver}'s FIB:\n")
        info(ndn.net[receiver].cmd(f"nfdc fib list"))

    for source in sources:
        # check if the server is running
        server_pid = ndn.net[source].cmd("pgrep -f ndn-traffic-server")
        if server_pid:
            info(f"Traffic server running on {source} with PID {server_pid}\n")
        else:
            info(f"WARNING: Traffic server not running on {source}!\n")
    
    # === STEP 2: Perform ndnpeek requests ===
    info("Starting DNS lookup requests...\n")

    
    # Setup circular buffer cache with fixed size
    CACHE_SIZE = 100
    caches = {}
    wrtie_indexs = {}
    for receiver in receivers:
        caches[receiver] = [[],] * CACHE_SIZE
        wrtie_indexs[receiver] = 0
        if not os.path.exists(f"{ndn.workDir}/{receiver}/peek-data"):
            os.makedirs(f"{ndn.workDir}/{receiver}/peek-data")
        

    
    # Process each DNS request
    for event in traffic:
        receiver = event["receiver"]
        domain = event["domain"]
        rtype = event["rtype"]
        # Construct the base prefix
        base_prefix = "/".join(domain.split(".")[::-1])
        
        # Construct the specific content name including the record type
        content_name = f"{base_prefix}" 
        timestamp = event["timestamp"]

        cache = caches[receiver]
        wrtie_index = wrtie_indexs[receiver]
        # Check cache
        for cache_entry in cache:
            if cache_entry and cache_entry[0] == domain.rstrip(".") and cache_entry[1] == rtype:
                info(f"CACHE HIT: Using cached result for {domain} {rtype}\n")
                info(f"Cached content: {cache_entry}\n")
                total_time += 0
                continue

        consumer = ndn.net[receiver]
        info(f"CACHE MISS: {receiver} Requesting {domain} {rtype} via {content_name}\n")
        # Revert back to consumer.cmd without explicit socket path
        # ndnpeek_cmd = "ndnpeek {} > peek-data/{}-{}.txt".format(content_name, domain, rtype)
        ndnpeek_cmd = f"ndnpeek -p {content_name} -v"
        # print(f"Executing command: {ndnpeek_cmd}\n")
        peek_output = consumer.cmd(ndnpeek_cmd)
        info(f"ndnpeek output\n: {peek_output}\n##########################")

        with open(f"{ndn.workDir}/{receiver}/peek-data/log.txt", "a") as f:
            f.write(f"Domain: {domain}, Rtype: {rtype}, Output: {peek_output}\n")

        # Extract RTT info from peek_output
        rtt = peek_output.split("RTT: ")[1].split("ms")[0]
        if rtt:
            total_time += float(rtt)
            info(f"RTT for {domain} {rtype}: {rtt} ms\n")


        
        # get the peek output file from the consumer a
        # consumer.cmd(f"mv peek-data/{domain}-{rtype}.txt {ndn.workDir}/{consumer.name}/peek-data/")

        
        # Check for errors in the output string
        if "ERROR" in peek_output or "Nack" in peek_output or "NoRoute" in peek_output:
             info(f"Warning: ndnpeek returned an error or Nack/NoRoute: {peek_output}\n")

        # Store in cache (only if successful - check for common failure indicators)
        if peek_output and "ERROR" not in peek_output and "Nack" not in peek_output and "NoRoute" not in peek_output:
            # parse peek_output to get the content
            records = [unparsed_rec.split("-") for unparsed_rec in peek_output.split("+")]
            for record in records:
                cache[wrtie_index] = record
                # info(f"Stored result in cache for {record[0]} {record[1]} at position {wrtie_index}\n")
                wrtie_index = (wrtie_index + 1) % CACHE_SIZE
            
        caches[receiver] = cache
        wrtie_indexs[receiver] = wrtie_index
        # sleep(2)

        # temp_path = "/home/mithilpn/projects/ndn-dns-exps/client-configs/client.conf"
        # for source in source_domain_map:
        #     if source_domain_map[source] == domain:
        #         server_config = f"{ndn.workDir}/{source}/server-config/{domain}-server.conf"
        #         # Create a temporary client config based on the server config
        #         make_temp_client_config(server_config, temp_path)
        #         # Copy the server config to the consumer's directory
        #         # shutil.copy(server_config, f"{ndn.workDir}/{receiver}/peek-data/")
        #         # Copy the temporary client config to the consumer's directory
        #         shutil.copy(temp_path, f"{ndn.workDir}/{receiver}/peek-data/client.conf")
        #         break
        # ndn.net[receiver].cmd(f"ndn-traffic-client -c {1} peek-data/client.conf > clinet-log.txt 2>&1 &")

        # make_temp_client_config(config_path_dst, temp_path)
        # else:
        #      # Store the failure indication in cache as well
        #      if cache_keys[cache_index] in cache_map:
        #          del cache_map[cache_keys[cache_index]]
             
        #      cache_keys[cache_index] = cache_key
        #      # Store a simplified error string based on output
        #      if "NoRoute" in peek_output:
        #          error_indication = "NoRoute"
        #      elif "Nack" in peek_output:
        #          error_indication = "Nack"
        #      elif "Timeout" in peek_output: # Check for timeout messages
        #          error_indication = "Timeout"
        #      elif "ERROR" in peek_output:
        #          error_indication = "Error"
        #      else: # Default fallback if output is empty or has unknown failure
        #          error_indication = "Timeout/Unknown"
        #      cache_values[cache_index] = error_indication 
        #      cache_map[cache_key] = cache_index
        #      cache_index = (cache_index + 1) % CACHE_SIZE
        #      info(f"Stored failure indication '{error_indication}' in cache for {domain} {rtype} at position {(cache_index-1) % CACHE_SIZE}\n")


    # Show ping server log to see if any requests were received
    # info("\nTraffic Server Logs:\n")
    # for source in sources:
    #     info(f"=== {source} Server Log ===\n")
    #     info(ndn.net[source].cmd("cat server-log.txt"))
    
    # === STEP 3: Show final peek results ===
    # info("\nFinal Cache Contents:\n")
    # for i in range(CACHE_SIZE):
    #     if cache[i]:  # Only show non-empty cache entries
    #         info(f"Position {i}: {cache[i]}\n")
    # info(f"Final cache write index: {wrtie_index}\n")
    # info("\nPeek Results from Files:\n")
    # all_results = consumer.cmd("cat peek-data/*")
    # info(all_results)
    
    # Cleanup
    # for host in ndn.net.hosts:
    #     host.cmd("rm -rf ./")
    
    print(f"########################################\nTotal time taken for all requests: {total_time} ms\n")
    print(f"Average time taken for all requests: {total_time / n_requests} ms\n")
    ndn.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()