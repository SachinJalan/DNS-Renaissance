import io
import sys
import csv
import os
import subprocess
import re
from datetime import datetime

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
        # if decoded.__class__.__name__ == "Raw":
        #     try:
        #         # Detect HTTP
        #         if decoded.haslayer(TCP) and decoded[TCP].dport == 80 or decoded[TCP].sport == 80:
        #             if HTTPRequest in decoded:
        #                 print("HTTPRequest!!!!!!!!!!!!!!!!!!!!\n")
        #                 http_req = decoded[HTTPRequest]
        #                 payload["class_name"] = "HTTPRequest"
        #                 payload["method"] = http_req.Method.decode()
        #                 payload["host"] = http_req.Host.decode() if http_req.Host else None
        #                 payload["path"] = http_req.Path.decode() if http_req.Path else None
        #                 payload["user_agent"] = http_req.User_Agent.decode() if http_req.User_Agent else None
        #                 packet["payload"].append(payload)
        #             elif HTTPResponse in decoded:
        #                 print("HTTPResponse!!!!!!!!!!!!!!!!!!!!\n")
        #                 http_res = decoded[HTTPResponse]
        #                 payload["class_name"] = "HTTPResponse"
        #                 payload["status_code"] = http_res.Status_Code.decode() if http_res.Status_Code else None
        #                 payload["server"] = http_res.Server.decode() if http_res.Server else None
        #                 packet["payload"].append(payload)
        #         # Detect TLS (SSL)
        #         elif decoded.haslayer(TCP) and decoded[TCP].dport == 443 or decoded[TCP].sport == 443:
        #             if TLSClientHello in decoded:
        #                 print("TLSClientHello!!!!!!!!!!!!!!!!!!!!\n")
        #                 tls_hello = decoded[TLSClientHello]
        #                 payload["class_name"] = "TLSClientHello"
        #                 payload["tls_version"] = tls_hello.version
        #                 payload["cipher_suites"] = [str(cs) for cs in tls_hello.cipher_suites]
        #                 packet["payload"].append(payload)
        #             elif TLSServerHello in decoded:
        #                 print("TLSServerHello!!!!!!!!!!!!!!!!!!!!\n")
        #                 tls_hello = decoded[TLSServerHello]
        #                 payload["class_name"] = "TLSServerHello"
        #                 payload["tls_version"] = tls_hello.version
        #                 payload["cipher_suite"] = str(tls_hello.cipher_suite)
        #                 packet["payload"].append(payload)
        #             if TLSApplicationData in decoded:
        #                 print("TLSApplicationData!!!!!!!!!!!!!!!!!!!!\n")
        #                 try:
        #                     payload["class_name"] += "TLSApplicationData"
        #                 except:
        #                     payload["class_name"] = "TLSApplicationData"
        #                 payload["data_length"] = len(decoded[TLSApplicationData].data)
        #                 packet["payload"].append(payload)
        #         else:
        #             payload["class_name"] = "Raw"
        #             packet["payload"].append(payload)

        #     except Exception as e:
        #         print(f"Error decoding payload: {e}")
        #     continue
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

def analyze_packets2(packets, master_doamin):
    results = {
        "master_domain": master_doamin,
        "Total Packets": 0,
        "Total Bytes": 0,
        "Total DNS Packets": 0,
        "Total DNS Bytes": 0,
        "Number of DNS Resolution": 0,
        "Total Time": 0,
        "Total DNS Time": 0,
        "last_packet_time": -1,
        "TTFB": -1,
        "start_time": -1,
        "Total DNS Cycles-core": -1,
        "Total DNS Cycles-atom": 0,
        "Total DNS Energy-pkg": -1,
        "Total DNS Energy-psys": -1,
        "Total DNS Energy-cores": -1,
        "domains": {},
    }   
    len_packets = len(packets)
    print("Total packets: ", len_packets)
    dns_cycles_core = 0
    dns_cycles_atom = 0
    dns_energy_pkg = 0
    dns_energy_psys = 0
    dns_energy_cores = 0
    domain_vals = {}
    for packet in packets:
        if results["start_time"] == -1:
            results["start_time"] = packet["timestamp"]

        if packet["payload"][-1]["class_name"] == "DNS": 
            domain = packet["payload"][-1]["qd"].split()[1].split("=")[1]

            # val_cycle = get_perf_cycles(domain=domain)
            # dns_cycles_atom += int(val_cycle[0])
            # dns_cycles_core += int(val_cycle[1])

            # val_energy = get_perf_energies(domain=domain)
            # dns_energy_pkg += float(val_energy[0])
            # dns_energy_psys += float(val_energy[1])
            # dns_energy_cores += float(val_energy[2])

            # print(packet["payload"][-1])

            if domain not in results["domains"]:
                results["domains"][domain] = {
                    "Total Packets": 0,
                    "Total Response Packets": 0,
                    "Total Query Packets": 0,
                    "qtypes": [],
                    "qclasses": [],
                    "rtypes": [],
                    "rclasses": [],
                }

            if packet["payload"][-1]["an"] != 'None':
                # DNS RESPONSE
                # if packet["payload"][-1]["ancount"]
                responses = packet["payload"][-1]["an"].split("|")
                # responses = responses.split("|")
                # print(responses)
                results["domains"][domain]["Total Response Packets"] += 1
                for response in responses:
                    # print(response)
                    if "rrname" not in response:
                        continue
                    rtype = response.split()[2].split("=")[1]
                    rclass = response.split()[3].split("=")[1]
                    results["domains"][domain]["rtypes"].append(rtype)
                    results["domains"][domain]["rclasses"].append(rclass)
                    print("Response:",domain, rtype, rclass)
            else:   
                qtype = packet["payload"][-1]["qd"].split()[2].split("=")[1]
                qclass = packet["payload"][-1]["qd"].split()[3].split("=")[1]
                results["domains"][domain]["Total Query Packets"] += 1
                results["domains"][domain]["qtypes"].append(qtype)
                results["domains"][domain]["qclasses"].append(qclass)
                print("Query:",domain, qtype, qclass)
                # if domain not in results["domains"]:
                # I chose to still measure energy again even if the domain has been visited before and caused a time out or not
                if (domain, qclass, qtype) not in domain_vals:
                    val_cycle = get_perf_cycles(domain=domain, qclass=qclass, qtype=qtype)
                    dns_cycles_atom += int(val_cycle[0])
                    dns_cycles_core += int(val_cycle[1])

                    val_energy = get_perf_energies(domain=domain, qclass=qclass, qtype=qtype)
                    dns_energy_pkg += float(val_energy[0])
                    dns_energy_psys += float(val_energy[1])
                    dns_energy_cores += float(val_energy[2])
                    domain_vals[(domain, qclass, qtype)] = (val_cycle, val_energy)
                else:
                    val_cycle = domain_vals[(domain, qclass, qtype)][0]
                    dns_cycles_atom += int(val_cycle[0])
                    dns_cycles_core += int(val_cycle[1])

                    val_energy = domain_vals[(domain, qclass, qtype)][1]
                    dns_energy_pkg += float(val_energy[0])
                    dns_energy_psys += float(val_energy[1])
                    dns_energy_cores += float(val_energy[2])
        
            results["domains"][domain]["Total Packets"] += 1


            # results["domains"].append(str(domain))

            results["Total Packets"] += 1
            results["Total Bytes"] += packet["packet_len"]
            results["Total DNS Packets"] += 1
            results["Total DNS Bytes"] += packet["packet_len"]
            if results["last_packet_time"] == -1:
                results["Total Time"] = (
                        (packet["timestamp"] - results["start_time"])*1000
                    )
                results["Total DNS Time"] = (
                        (packet["timestamp"] - results["start_time"])*1000
                    )
                results["last_packet_time"] = packet["timestamp"]
            else:
                results["Total Time"] += (
                        (packet["timestamp"] - results["last_packet_time"])*1000
                    )
                results["Total DNS Time"] += (
                        (packet["timestamp"] - results["last_packet_time"])*1000
                    )
                results["last_packet_time"] = packet["timestamp"]

        else:
            results["Total Packets"] += 1
            results["Total Bytes"] += packet["packet_len"]
            if results["last_packet_time"] == -1:
                results["Total Time"] = (
                        (packet["timestamp"] - results["start_time"])*1000
                    )
                results["last_packet_time"] = packet["timestamp"]
            else:
                results["Total Time"] += (
                        (packet["timestamp"] - results["last_packet_time"])*1000
                    )
                results["last_packet_time"] = packet["timestamp"]
            # if results["TTFB"] == -1:
            #     results["TTFB"] = (
            #             (packet["timestamp"] - results[domain]["start_time"])*1000
            #         )
            # break
            for payload in packet["payload"]:
                class_name = payload["class_name"]
                if class_name == "HTTPResponse":
                    # results["Total Packets}"] += 1
                    # results["Total Bytes"] += packet["packet_len"]
                    # if results["last_packet_time"] == -1:
                    #     results["Total Time"] = (
                    #             (packet["timestamp"] - results[domain]["start_time"])*1000
                    #         )
                    #     results["last_packet_time"] = packet["timestamp"]
                    # else:
                    #     results["Total Time"] += (
                    #             (packet["timestamp"] - results[domain]["last_packet_time"])*1000
                    #         )
                    #     results["last_packet_time"] = packet["timestamp"]
                    if results["TTFB"] == -1:
                        results["TTFB"] = (
                                (packet["timestamp"] - results["start_time"])*1000
                            )
                    break

                elif class_name == "TLS":
                    if payload["type"] == "application_data":
                        if results["TTFB"] == -1:
                            results["TTFB"] = (
                                    (packet["timestamp"] - results["start_time"])*1000
                                )
                    # results["Total Packets}"] += 1
                    # results["Total Bytes"] += packet["packet_len"]
                    # if results["last_packet_time"] == -1:
                    #     results["Total Time"] = (
                    #             (packet["timestamp"] - results[domain]["start_time"])*1000
                    #         )
                    #     results["last_packet_time"] = packet["timestamp"]
                    # else:
                    #     results["Total Time"] += (
                    #             (packet["timestamp"] - results[domain]["last_packet_time"])*1000
                    #         )
                    #     results["last_packet_time"] = packet["timestamp"]
                    break

                elif class_name == "_TLSEncryptedContent":
                    # results["Total Packets}"] += 1
                    # results["Total Bytes"] += packet["packet_len"]
                    # if results["last_packet_time"] == -1:
                    #     results["Total Time"] = (
                    #             (packet["timestamp"] - results[domain]["start_time"])*1000
                    #         )
                    #     results["last_packet_time"] = packet["timestamp"]
                    # else:
                    #     results["Total Time"] += (
                    #             (packet["timestamp"] - results[domain]["last_packet_time"])*1000
                    #         )
                    #     results["last_packet_time"] = packet["timestamp"]
                    if results["TTFB"] == -1:
                        results["TTFB"] = (
                                (packet["timestamp"] - results["start_time"])*1000
                            )
                    break

        # calculate number of resolution
        # if packet["payload"][-1]["class_name"] == "DNS":
        #     results["Number of DNS Resolution"] += 1
        #     print(packet)


    if dns_cycles_core != 0:
        results["Total DNS Cycles-core"] = dns_cycles_core
    results["Total DNS Cycles-atom"] = dns_cycles_atom
    results["Total DNS Energy-pkg"] = dns_energy_pkg
    results["Total DNS Energy-psys"] = dns_energy_psys
    results["Total DNS Energy-cores"] = dns_energy_cores
    return results

def analyze_packets(packets):
    results = {}
    domain = ""
    len_packets = len(packets)
    print("Total packets: ", len_packets)
    i = 0
    while i < len_packets:
        packet = packets[i]
        if packet["payload"][-1]["class_name"] == "DNS":
            if packet["payload"][-1]["ancount"] == "0":
                domain = packet["payload"][-1]["qd"].split()[1].split("=")[1]
                results[domain] = {
                    "Total Packets": 0,
                    "Total Bytes": 0,
                    "Total DNS Packets": 0,
                    "Total DNS Bytes": 0,
                    "Total Time": 0,
                    "Total DNS Time": 0,
                    "last_packet_time": packet["timestamp"],
                    "TTFB": -1,
                    "start_time": packet["timestamp"],
                }
                while i < len_packets:
                    packet = packets[i]
                    if packet["payload"][-1]["class_name"] == "DNS":
                        if (
                            packet["payload"][-1]["qd"].split()[1].split("=")[1]
                            != domain
                        ):
                            i = i - 1
                            break
                        results[domain]["Total DNS Packets"] += 1
                        results[domain]["Total DNS Bytes"] += packet["packet_len"]
                        results[domain]["Total DNS Time"] += (
                            (packet["timestamp"] - results[domain]["last_packet_time"])*1000
                        )
                    else:
                        if results[domain]["TTFB"] == -1:
                            for payload in packet["payload"]:
                                class_name = payload["class_name"]
                                if "HTTPResponse" == class_name:
                                    results[domain]["TTFB"] = (
                                        (packet["timestamp"] - results[domain]["start_time"])*1000
                                    )
                                elif class_name == "TLS":
                                    if payload["type"] == "application_data":
                                        results[domain]["TTFB"] = (
                                            (packet["timestamp"] - results[domain]["start_time"])*1000
                                        )   
                                elif class_name == "_TLSEncryptedContent":
                                    results[domain]["TTFB"] = (
                                        (packet["timestamp"] - results[domain]["start_time"])*1000
                                    )                                                                  
                            # if "HTTPResponse" in [payload["class_name"] for payload in packet["payload"]]:
                            #     results[domain]["TTFB"] = (
                            #         (packet["timestamp"] - results[domain]["start_time"])*1000
                            #     )
                            # elif "TLS" in [payload["class_name"] for payload in packet["payload"]]:
                            #     for 
                            #     results[domain]["TTFB"] = (
                            #         (packet["timestamp"] - results[domain]["start_time"])*1000
                            #     )

                    results[domain]["Total Packets"] += 1
                    results[domain]["Total Bytes"] += packet["packet_len"]
                    results[domain]["Total Time"] += (
                        (packet["timestamp"] - results[domain]["last_packet_time"])*1000
                    )
                    results[domain]["last_packet_time"] = packet["timestamp"]

                    i += 1
        i += 1

    return results

def save_results_to_csv(results, output_file):
    # Define the header based on the result dictionary keys
    headers = [
        "Domain",
        "Total Packets",
        "Total Bytes",
        "Total DNS Packets",
        "Total DNS Bytes",
        "Total Time",
        "Total DNS Time",
        "TTFB",
        "Total DNS Cycles-core",
        "Total DNS Cycles-atom",
        "Total DNS Energy-pkg",
        "Total DNS Energy-psys",
        "Total DNS Energy-cores",
        "Visited Domains",
    ]
    print(results)
    # Write the CSV file
    with open(output_file, mode="a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        # writer.writeheader()
        row = {
            "Domain": results["master_domain"],
            "Total Packets": results["Total Packets"],
            "Total Bytes": results["Total Bytes"],
            "Total DNS Packets": results["Total DNS Packets"],
            "Total DNS Bytes": results["Total DNS Bytes"],
            "Total Time": results["Total Time"],
            "Total DNS Time": results["Total DNS Time"],
            "TTFB": results["TTFB"],
            "Total DNS Cycles-core": results["Total DNS Cycles-core"],
            "Total DNS Cycles-atom": results["Total DNS Cycles-atom"],
            "Total DNS Energy-pkg": results["Total DNS Energy-pkg"],
            "Total DNS Energy-psys": results["Total DNS Energy-psys"],
            "Total DNS Energy-cores": results["Total DNS Energy-cores"],
            "Visited Domains": results["domains"]
        }
        writer.writerow(row)

def get_perf_cycles(domain, qclass, qtype):
    perf_command = ['perf', 'stat', '-e', 'cycles', 'dig', '+trace', '-c', qclass, '-t', qtype, domain]
    result = subprocess.run(perf_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, )
    perf_output = result.stderr
    # print(perf_output)
    match_core = re.search(r'([\d,]+)\s+cpu_core/cycles:u/', perf_output)
    if match_core:
        cycles_core = int(match_core.group(1).replace(',', ''))
    else:
        raise ValueError(f"Could not find cycles-core information in perf output for domain {domain}")
    
    match_atom = re.search(r'([\d,]+)\s+cpu_atom/cycles:u/', perf_output)
    if match_atom:
        cycles_atom = int(match_atom.group(1).replace(',', ''))
    else:
        raise ValueError(f"Could not find cycles-atom information in perf output for domain {domain}")
    
    return cycles_atom, cycles_core
    
def get_perf_energies(domain, qclass, qtype):
    # Run the 'perf' command with 'dig +trace' and capture the output
    perf_command = ['sudo', 'perf', 'stat', '-e', 'power/energy-pkg/,power/energy-psys/,power/energy-cores/', 'dig', '+trace', '-c', qclass, '-t', qtype, domain]
    result = subprocess.run(perf_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    perf_output = result.stderr
    
    # Extract energy from CPU package (power/energy-pkg/)
    match_pkg = re.search(r'([\d,\.]+)\s+Joules\s+power/energy-pkg/', perf_output)
    if match_pkg:
        energy_pkg = float(match_pkg.group(1).replace(',', ''))
    else:
        raise ValueError(f"Could not find energy-pkg information in perf output for domain {domain}")

    # Extract energy from platform (power/energy-psys/)
    match_psys = re.search(r'([\d,\.]+)\s+Joules\s+power/energy-psys/', perf_output)
    if match_psys:
        energy_psys = float(match_psys.group(1).replace(',', ''))
    else:
        raise ValueError(f"Could not find energy-psys information in perf output for domain {domain}")
    
    match_cores = re.search(r'([\d,\.]+)\s+Joules\s+power/energy-cores/', perf_output)
    if match_cores:
        energy_cores = float(match_cores.group(1).replace(',', ''))
    else:
        raise ValueError(f"Could not find energy-cores information in perf output for domain {domain}")
    return energy_pkg, energy_psys, energy_cores

def main():
    # if len(sys.argv) < 3:
    #     print("Usage: python pcapng-analyzer.py <pcapng_file> <domain.name>")
    #     sys.exit(1)
    # pcapng_file = sys.argv[1]

    DIR_PATH = "./pcapngs"
    pcangs =  os.listdir(DIR_PATH)
    # output_file = "results3.csv"
    output_file = "results-test.csv"
    # Analyze the results2.csv for the already doen domains:
    # analyzed_domains = []
    # with open(output_file, "r") as csvfile:
    #     reader = csv.reader(csvfile)
    #     for row in reader:
    #         analyzed_domains.append(row[0])
    #         print(row[0])

    # print("Number of already analyzed domains: ", len(analyzed_domains))

    headers = [
        "Domain",       
        "Total Packets",
        "Total Bytes",
        "Total DNS Packets",
        "Total DNS Bytes",
        "Total Time",
        "Total DNS Time",
        "TTFB",
        "Total DNS Cycles-core",
        "Total DNS Cycles-atom",
        "Total DNS Energy-pkg",
        "Total DNS Energy-psys",
        "Total DNS Energy-cores",
        "Visited Domains",
    ]

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
        results = analyze_packets2(packets, domain)
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
