# filepath: generate_query_log.py
from datetime import datetime, timedelta
import time
# Define the output file
output_file = "/home/mithilpn/projects/ndn-dns-exps/query.log"

# Define the domains and record types
domains = ["google.com", "iitgn.ac.in"]
record_types = ["A", "AAAA"]

# Start time from now
start_time = datetime.now()

# Generate log entries
with open(output_file, "w") as f:
    for i in range(100):  # Generate 100 entries
        timestamp = (start_time + timedelta(minutes=i)).isoformat() + "+00:00"
        domain = domains[i % len(domains)]
        record_type = record_types[i % len(record_types)]
        f.write(f"{timestamp} '{domain}.' type '{record_type}'\n")

print(f"Query log generated: {output_file}")