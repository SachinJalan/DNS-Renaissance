import csv
import subprocess
import re

def run_dig(subdomain):
    """Runs the dig command to fetch NS records for the given subdomain."""
    try:
        print(f"Running dig for {subdomain}")
        result = subprocess.run(["dig", subdomain, "-t", "NS"], capture_output=True, text=True, check=True)
        # Debugging: Print the dig output
        # print("=== DIG OUTPUT START ===")
        # print(result.stdout)
        # print("=== DIG OUTPUT END ===")
        soa_pattern = re.search(r"(\S+)\s+\d+\s+IN\s+SOA\s+(\S+)", result.stdout)

        if soa_pattern:
            # domain = soa_pattern.group(1)  # The domain name (e.g., iitgn.ac.in.)
            primary_ns = soa_pattern.group(2)  # The primary NS (e.g., dnsm.iitgn.ac.in.)
            return primary_ns
        
    except subprocess.CalledProcessError as e:
        print(f"Error running dig for {subdomain}: {e}")
        return None

# def extract_info(dig_output):
#     """Extracts the SOA record primary NS from dig output."""
#     if not dig_output:
#         return None

#     # Debugging: Print the dig output
#     # print("=== DIG OUTPUT START ===")
#     # print(dig_output)
#     # print("=== DIG OUTPUT END ===")

#     # Use regex to find the SOA record in the AUTHORITY SECTION
#     soa_pattern = re.search(r"(\S+)\s+\d+\s+IN\s+SOA\s+(\S+)", dig_output)

#     if soa_pattern:
#         # domain = soa_pattern.group(1)  # The domain name (e.g., iitgn.ac.in.)
#         primary_ns = soa_pattern.group(2)  # The primary NS (e.g., dnsm.iitgn.ac.in.)
#         return primary_ns

#     return None  # Return None if no SOA record is found

def process_csv(input_csv, output_csv):
    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        with open(output_csv, 'w', newline='') as outfile:
            fieldnames = ["Subdomain", "IP", "SOA-Primary-NS"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                subdomain = row["Subdomain"].strip()
                primary_ns = run_dig(subdomain)
                
                writer.writerow({
                    "Subdomain": subdomain,
                    "IP": row["IP"],
                    "SOA-Primary-NS": primary_ns
                })
                
if __name__ == "__main__":
    process_csv("/home/mithilpn/Projects/project-course-dns/DNS-Renaissance/iiti_ac_in_subdomains_corrected.csv", "/home/mithilpn/Projects/project-course-dns/DNS-Renaissance/iiti_ac_in_subdomains_with_ns.csv")

# import subprocess
# import re

# def run_dig(subdomain):
#     """Runs the dig command to fetch NS records for the given subdomain."""
#     try:
#         print(f"Running dig for {subdomain}")
#         result = subprocess.run(["dig", subdomain, "-t", "NS"], capture_output=True, text=True, check=True)
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         print(f"Error running dig for {subdomain}: {e}")
#         return None

# def extract_info(dig_output):
#     """Extracts the SOA record primary NS from dig output."""
#     if not dig_output:
#         return None

#     # Debugging: Print the dig output
#     # print("=== DIG OUTPUT START ===")
#     # print(dig_output)
#     # print("=== DIG OUTPUT END ===")

#     # Use regex to find the SOA record in the AUTHORITY SECTION
#     soa_pattern = re.search(r"(\S+)\s+\d+\s+IN\s+SOA\s+(\S+)", dig_output)

#     if soa_pattern:
#         domain = soa_pattern.group(1)  # The domain name (e.g., iitgn.ac.in.)
#         primary_ns = soa_pattern.group(2)  # The primary NS (e.g., dnsm.iitgn.ac.in.)
#         return {
#             "domain": domain,
#             "primary_ns": primary_ns
#         }

#     return None  # Return None if no SOA record is found

# # Example usage
# subdomain = "www.alumni.iitgn.ac.in"
# dig_output = run_dig(subdomain)
# info = extract_info(dig_output)

# if info:
#     print(f"Primary NS for {info['domain']}: {info['primary_ns']}")
# else:
#     print(f"No SOA record found for {subdomain}")

