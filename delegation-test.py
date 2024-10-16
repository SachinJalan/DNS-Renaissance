import io
import sys
import csv
import os
import subprocess
import re
from datetime import datetime
import time

# To make sure all packet types are available
import scapy.all  # noqa
import scapy.packet
from scapy.layers.l2 import Ether
from scapy.layers.http import HTTP
from scapy.layers.inet import TCP
from scapy.layers.tls.all import TLS
import pcapng
from pcapng.blocks import EnhancedPacket, InterfaceDescription, SectionHeader


def get_packets(scanner):
    packets = []
    i = 0
    for block in scanner:
        if isinstance(block, SectionHeader):
            continue
        elif isinstance(block, InterfaceDescription):
            continue
        elif isinstance(block, EnhancedPacket):
            # if i == 12:
            #     break
            packets.append(extract_enhanced_packet(block))
            i += 1
        else:
            continue
    return packets


def extract_enhanced_packet(block):
    packet = {}
    packet["timestamp"] = block.timestamp
    packet["packet_len"] = block.packet_len
    decoded = Ether(block.packet_data)
    packet["src_mac"] = decoded.src
    packet["dst_mac"] = decoded.dst
    packet["type"] = decoded.type
    packet["payload"] = []
    while decoded.payload:
        decoded = decoded.payload
        payload = {}
        payload["class_name"] = decoded.__class__.__name__
        for f in decoded.fields_desc:
            if f.name in decoded.fields:
                val = f.i2repr(decoded, decoded.fields[f.name])
            elif f.name in decoded.overloaded_fields:
                val = f.i2repr(decoded, decoded.overloaded_fields[f.name])
            else:
                continue
            payload[f.name] = val
        packet["payload"].append(payload)
    # print(packet)
    return packet

def cmp_resolution_methods(packets, domain):
    results = {
        "master_domain":domain,
        "total_recursive":0,
        "total_iterative":0,
        "total_delegated":0,
        "domains":{},
    }
    domain_vals = {}
    for packet in packets:
        if packet["payload"][-1]["class_name"] == "DNS":
            if packet["payload"][-1]["an"] == 'None': 
                domain = str(packet["payload"][-1]["qd"].split()[1].split("=")[1])
                qtype = str(packet["payload"][-1]["qd"].split()[2].split("=")[1])
                qclass = str(packet["payload"][-1]["qd"].split()[3].split("=")[1])
                if (domain,qclass,qtype) not in domain_vals:
                    vals = get_resolution_times(domain=domain, qclass=qclass, qtype=qtype)
                    domain_vals[(domain,qclass,qtype)] = vals
                    results["domains"][domain] = {
                        "recursive": vals[0],
                        "iterative": vals[1],
                        "delegated": vals[2],
                        "count": 1,
                    }
                    results["total_recursive"] += vals[0]
                    results["total_iterative"] += vals[1]
                    if vals[2]:
                        if results["total_delegated"]:
                            results["total_delegated"] += vals[2]
                    else:
                        results["total_delegated"] = None
                    # results["total_delegated"] += vals[2]

                else:
                    vals = domain_vals[(domain,qclass,qtype)]
                    results["domains"][domain]["recursive"] += vals[0]
                    results["domains"][domain]["iterative"] += vals[1]
                    if vals[2]:
                        if results["domains"][domain]["delegated"]:
                            results["domains"][domain]["delegated"] += vals[2]
                    else:
                        results["domains"][domain]["delegated"] = None
                    # results["domains"][domain]["delegated"] += vals[2]
                    results["domains"][domain]["count"] += 1
                    results["total_recursive"] += vals[0]
                    results["total_iterative"] += vals[1]
                    if vals[2]:
                        if results["total_delegated"]:
                            results["total_delegated"] += vals[2]
                    else:
                        results["total_delegated"] = None
                print(f"Domain: {domain}, Class: {qclass}, Type: {qtype}, Recursive: {vals[0]}, Iterative: {vals[1]}, Delegated: {vals[2]}")
    return results

# def get_resolution_times(domain, qclass, qtype):

#     dig_trace_command = ['dig', '@8.8.8.8', '+trace', '-c', qclass, '-t', qtype, domain]
#     dig_command_iterative = ['dig', '@8.8.8.8', '+norecurse', '-c', qclass, '-t', qtype, domain]
#     dig_command_recursive = ['dig', '@8.8.8.8', '+recurse', '-c', qclass, '-t', qtype, domain]

#     result = subprocess.run(dig_command_iterative, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
#     time_match = re.search(r';; Query time: (\d+) ms', result.stdout)
#     time_iterative = float(time_match.group(1)) if time_match else None

#     result = subprocess.run(dig_command_recursive, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
#     time_match = re.search(r';; Query time: (\d+) ms', result.stdout)
#     time_recursive = float(time_match.group(1)) if time_match else None

#     result_trace = subprocess.run(dig_trace_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
#     lines = result_trace.stdout.split("\n")
#     ns_server_ip = lines[-3].split()[5].split("#")[0]

#     if ns_server_ip:
#         # print("IP:", ns_server_ip)
#         ping_command = ['sudo', 'hping3', '-c', '3', '-S', '-p', '53', ns_server_ip]
#         result = subprocess.run(ping_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
#         # print(result.stdout)
#         time_match = re.findall(r'rtt=(\d+\.\d+) ms', result.stdout)
#         time_delegated = None
#         if time_match:
#             # print("PING TIMES (individual):", time_match)
#             avg_ping_time = sum(float(t) for t in time_match) / len(time_match)
#             print("PING TIME (avg):", avg_ping_time, "IP: ", ns_server_ip)
#             time_delegated = 0.5 * avg_ping_time + 0.5 * time_recursive if time_recursive else None
#             # print("Time Delegated:", time_delegated)
#         else:
#             print("No ping time found.")
#     else:
#         print("No authoritative NS server found.")
#         time_delegated = None
#     return (time_recursive, time_iterative, time_delegated)

def get_resolution_times(domain, qclass, qtype):
    domain = domain[1:-1]
    # print(domain)
    # DIG commands for different resolution methods
    ns_command = ['dig','+short', '-c', qclass, '-t', 'NS', domain]
    dig_command_iterative = ['dig', '@8.8.8.8', '+norecurse', '-c', qclass, '-t', qtype, domain]
    dig_command_recursive = ['dig', '@8.8.8.8', '+recurse', '-c', qclass, '-t', qtype, domain]

    # Iterative resolution time
    result = subprocess.run(dig_command_iterative, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    time_match = re.search(r';; Query time: (\d+) ms', result.stdout)
    time_iterative = float(time_match.group(1)) if time_match else None

    time.sleep(2)

    # Recursive resolution time
    result = subprocess.run(dig_command_recursive, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    time_match = re.search(r';; Query time: (\d+) ms', result.stdout)
    time_recursive = float(time_match.group(1)) if time_match else None

    result_ns = subprocess.run(ns_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    print(f"[DEBUG] Domain: {domain} ns_result output: {result_ns.stdout}")

    # Split the output into lines
    lines = result_ns.stdout.split("\n")

    ns_server_ip = None

    # Loop through the lines to process each NS record
    for line in lines:
        if line.strip():  # Skip empty lines
            # Run dig to resolve the NS domain into an IP
            ns_command_2 = ['dig', '+short', line.strip()]
            result_ns_2 = subprocess.run(ns_command_2, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            ns_server_ip = result_ns_2.stdout.strip()  # Get the IP address

            # Stop after finding the first NS IP
            if ns_server_ip:
                break

    if ns_server_ip:
        # Ping the NS server with hping3
        ping_command = ['sudo', 'hping3', '-c', '3', '-S', '-p', '53', ns_server_ip]
        result = subprocess.run(ping_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        print(f"[DEBUG] Domain: {domain}, Ns server IP: {ns_server_ip} hping3 output: {result.stdout}")
        time_match = re.findall(r'rtt=(\d+\.\d+) ms', result.stdout)
        time_delegated = None
        
        if time_match:
            # Calculate average ping time
            avg_ping_time = sum(float(t) for t in time_match) / len(time_match)
            print(f"[DEBUG] Domain: {domain}, Ns server IP: {ns_server_ip} PING TIME (avg): {avg_ping_time} ms, IP: {ns_server_ip}")
            time_delegated = 0.5 * avg_ping_time + 0.5 * time_recursive if time_recursive else None
        else:
            print("No ping time found.")
    else:
        print("No authoritative NS server found.")
        time_delegated = None
    
    return float(time_recursive), float(time_iterative), time_delegated


def save_results_to_csv(results, output_file):
    # Define the header based on the result dictionary keys
    headers = ["Domain", "Recursive", "Iterative", "Delegated","Visited domains"]
    print(results)
    # Write the CSV file
    with open(output_file, mode="a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        # writer.writeheader()
        row = {
            "Domain": results["master_domain"],
            "Recursive": results["total_recursive"],
            "Iterative": results["total_iterative"],
            "Delegated": results["total_delegated"],
            "Visited domains":results["domains"],
        }
        writer.writerow(row)

def main():
    # get_resolution_times("'iitgn.ac.in.'", "IN", "A")
    DIR_PATH = "./pcapngs2"
    pcangs =  os.listdir(DIR_PATH)
    output_file = "results-time-test-2.csv"
    # analyzed_domains = []
    # with open("results-test.csv", "r") as csvfile:
    #     reader = csv.reader(csvfile)
    #     for row in reader:
    #         analyzed_domains.append(row[0])
    #         print(row[0])

    # print("Number of already analyzed domains: ", len(analyzed_domains))
    # headers = ["domain", "recursive", "iterative", "delegated", "count"]
    headers = ["Domain", "Recursive", "Iterative", "Delegated","Visited domains"]


    # Write the CSV file
    with open(output_file, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

    for pcapng_file in pcangs:
        pcapng_file = DIR_PATH + f"/{pcapng_file}"
        domain = os.path.basename(pcapng_file)[:-7]
        # if domain in analyzed_domains:
        #     print(f"{domain} already analyzed. Skipping...")
        #     continue
        # output_file = "results.csv"  # Change output file to CSV format
        packets = []
        with open(pcapng_file, "rb") as fp:
            scanner = pcapng.FileScanner(fp)
            packets = get_packets(scanner)

        print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")
        print(f"EXTRACTION COMPLETE FOR {domain}")
        print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")
        results = cmp_resolution_methods(packets, domain)
        print(f"ANALYSIS COMPLETE FOR {domain}")
        print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")

        # Save the results to a CSV file instead of JSON
        save_results_to_csv(results, output_file)
        print(f"RESULTS FOR {domain} SAVED IN {output_file}")
        print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")

        # Print the results from the CSV for verification
        # with open(output_file, "r") as csvfile:
        #     reader = csv.reader(csvfile)
        #     for row in reader:
        #         print(", ".join(row))


if __name__ == "__main__":
    main()
