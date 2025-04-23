import os
import csv
import argparse
from collections import defaultdict

def create_directories(base_dir):
    """Create the necessary directory structure for DNS configurations"""
    os.makedirs(os.path.join(base_dir, "root", "zones"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "tld"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "auth"), exist_ok=True)

def create_root_config(base_dir, tlds):
    """Generate root server configuration files"""
    # Create named.conf
    named_conf_path = os.path.join(base_dir, "root", "named.conf")
    with open(named_conf_path, "w") as f:
        f.write("""options {
    directory "/var/named";
    listen-on port 53 { any; };
    allow-query { any; };
    recursion no;
};

zone "." {
    type master;
    file "/var/named/root.zone";
};
""")
    
    # Create root zone file
    root_zone_path = os.path.join(base_dir, "root", "zones", "root.zone")
    with open(root_zone_path, "w") as f:
        f.write("""$TTL 86400
.       IN      SOA     root-server. admin.root-server. (
                        2023121001      ; serial
                        3600            ; refresh
                        1800            ; retry
                        604800          ; expire
                        86400           ; minimum TTL
                        )
        IN      NS      root-server.

""")
        
        # Add TLD delegations
        for tld in tlds:
            f.write(f"{tld}.    IN      NS      tld-server-{tld}.\n")
            f.write(f"{tld}.    IN      A       192.168.0.{50 + tlds.index(tld)}  ; Placeholder IP\n")

    print(f"Root server configuration generated at {named_conf_path}")

def create_tld_config(base_dir, tld, domains):
    """Generate TLD server configuration files"""
    # Create TLD directory and zones directory
    tld_dir = os.path.join(base_dir, "tld", tld)
    os.makedirs(os.path.join(tld_dir, "zones"), exist_ok=True)
    
    # Create named.conf
    named_conf_path = os.path.join(tld_dir, "named.conf")
    with open(named_conf_path, "w") as f:
        f.write(f"""options {{
    directory "/var/named";
    listen-on port 53 {{ any; }};
    allow-query {{ any; }};
    recursion no;
}};

zone "{tld}" {{
    type master;
    file "/var/named/{tld}.zone";
}};
""")
    
    # Create zone file
    zone_path = os.path.join(tld_dir, "zones", f"{tld}.zone")
    with open(zone_path, "w") as f:
        f.write(f"""$TTL 86400
{tld}.   IN      SOA     tld-server-{tld}. admin.tld-server-{tld}. (
                        2023121001      ; serial
                        3600            ; refresh
                        1800            ; retry
                        604800          ; expire
                        86400           ; minimum TTL
                        )
        IN      NS      tld-server-{tld}.

""")
        
        # Add domain delegations
        for i, domain in enumerate(domains):
            domain_label = domain.rstrip('.').split('.')[-2]  # Get the domain part before TLD
            f.write(f"{domain_label}.{tld}.    IN      NS      auth-server-{domain_label}-{tld}.\n")
            f.write(f"{domain_label}.{tld}.    IN      A       192.168.0.{100 + i}  ; Placeholder IP\n")
    
    print(f"TLD server configuration for .{tld} generated at {named_conf_path}")

def create_auth_config(base_dir, domain, records):
    """Generate authoritative server configuration files"""
    # Strip trailing dot if present
    domain_clean = domain.rstrip('.')
    
    # Create directory structure
    auth_dir = os.path.join(base_dir, "auth", domain_clean)
    os.makedirs(os.path.join(auth_dir, "zones"), exist_ok=True)
    
    # Create named.conf
    named_conf_path = os.path.join(auth_dir, "named.conf")
    with open(named_conf_path, "w") as f:
        f.write(f"""options {{
    directory "/var/named";
    listen-on port 53 {{ any; }};
    allow-query {{ any; }};
    recursion no;
}};

zone "{domain_clean}" {{
    type master;
    file "/var/named/{domain_clean}.zone";
}};
""")
    
    # Create zone file
    zone_path = os.path.join(auth_dir, "zones", f"{domain_clean}.zone")
    with open(zone_path, "w") as f:
        f.write(f"""$TTL 86400
{domain}    IN      SOA     auth-server-{domain_clean.replace('.', '-')}. admin.{domain} (
                        2023121001      ; serial
                        3600            ; refresh
                        1800            ; retry
                        604800          ; expire
                        86400           ; minimum TTL
                        )
                IN      NS      auth-server-{domain_clean.replace('.', '-')}.

""")
        
        # Add records from DNS recon results
        for record in records:
            rtype = record[1]
            name = record[2]
            address = record[3]
            target = record[4]
            
            # Format the record depending on its type
            if rtype == "A":
                f.write(f"{name}    IN      A       {address}\n")
            elif rtype == "AAAA":
                f.write(f"{name}    IN      AAAA    {address}\n")
            elif rtype == "CNAME":
                f.write(f"{name}    IN      CNAME   {target}.\n")
            elif rtype == "MX":
                priority = 10  # Default priority
                f.write(f"{name}    IN      MX      {priority} {target}.\n")
            elif rtype == "TXT":
                # Clean up the string value
                string_val = record[6].replace('"', '\\"')
                f.write(f'{name}    IN      TXT     "{string_val}"\n')
            elif rtype == "NS":
                f.write(f"{name}    IN      NS      {target}.\n")
            elif rtype == "SOA":
                # SOA records are already handled above
                pass
            else:
                # Generic record format for other types
                f.write(f"{name}    IN      {rtype}   {address if address else target}\n")
    
    print(f"Authoritative server configuration for {domain} generated at {named_conf_path}")

def process_domains(domain_file, results_dir, output_dir):
    """Process domain list and generate DNS configurations"""
    # Create base directory structure
    create_directories(output_dir)
    
    # Read domain list
    with open(domain_file, "r") as f:
        domains = [line.strip() for line in f.readlines()]
    
    # Group domains by TLD
    tld_domains = defaultdict(list)
    all_records = {}
    
    for domain in domains:
        # Ensure domain ends with a dot
        if domain[-1] != ".":
            domain += "."
        
        # Extract TLD
        parts = domain.split(".")
        if len(parts) >= 3:  # Need at least one label plus TLD plus empty string
            tld = parts[-2]  # Second last part (before empty string after last dot)
            tld_domains[tld].append(domain)
        
        # Read DNS records from CSV
        csv_file = os.path.join(results_dir, f"{domain.rstrip('.')}.csv")
        if not os.path.exists(csv_file):
            print(f"CSV file for {domain} not found in {results_dir}.")
            continue
        
        records = []
        with open(csv_file, "r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                records.append(row)
        
        all_records[domain] = records
    
    # Generate root server config with all TLDs
    create_root_config(output_dir, list(tld_domains.keys()))
    
    # Generate TLD server configs
    for tld, domains in tld_domains.items():
        create_tld_config(output_dir, tld, domains)
    
    # Generate authoritative server configs
    for domain, records in all_records.items():
        create_auth_config(output_dir, domain, records)
    
    print(f"All DNS configurations have been generated in {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate hierarchical DNS server configurations")
    parser.add_argument("-d", help="domain.txt file with list of domains")
    parser.add_argument("-s", help="source directory with the dnsrecon results")
    parser.add_argument("-o", help="output directory to store DNS configuration files")
    args = parser.parse_args()

    domain_txt = args.d
    source_dir = args.s
    output_dir = args.o
    
    if not domain_txt or not source_dir or not output_dir:
        print("Please provide all required arguments: -d, -s, -o")
        exit(1)
    
    process_domains(domain_txt, source_dir, output_dir)
