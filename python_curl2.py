import csv
import subprocess
import os
import signal
import time
# Path to the CSV file
csv_file_path = 'new_data.csv'

# Timeout duration in seconds (for wget)
timeout_duration = 10

# Network interface to capture
interface = 'eth0'

# Read the CSV file and extract domain names
with open(csv_file_path, mode='r') as file:
    csv_reader = csv.reader(file)
    
    for row in csv_reader:
        domain = row[0]  # Assuming domain names are in the first column
        full_domain = f"{domain}"
        print(f"Requesting {full_domain} with wget, timeout of {timeout_duration} seconds")
        
        # Start dumpcap process and save in pcapng format
        pcap_file = f"{domain}.pcapng"
        dumpcap_process = subprocess.Popen(
            ['dumpcap', '-i', interface, '-w', pcap_file, '-n'],  # '-n' saves in pcapng format
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(f"Started dumpcap for {full_domain}, saving to {pcap_file}")
        
        # Perform wget request with timeout and other flags
        result = subprocess.run(
            ['wget', '--no-dns-cache', '-c', '-E', '-H', '-k', '-K', '-p',
             f'--timeout={timeout_duration}', f'--read-timeout={timeout_duration}', '-t 1', full_domain],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            print(f"Successfully requested {full_domain}")
        else:
            print(f"Error requesting {full_domain}: {result.stderr.decode()}")
        time.sleep(4)
        # Wait for wget to complete, then stop dumpcap
        print(f"Stopping dumpcap for {full_domain}...")
        dumpcap_process.terminate()  # Gracefully stop dumpcap
        
        try:
            dumpcap_process.wait(timeout=5)  # Wait for it to close
            print(f"Stopped dumpcap for {full_domain}")
        except subprocess.TimeoutExpired:
            print(f"Dumpcap did not terminate in time for {full_domain}, force killing it.")
            dumpcap_process.kill()  # Force kill if it doesn't stop
        
        print(f"Finished processing {full_domain}\n")
