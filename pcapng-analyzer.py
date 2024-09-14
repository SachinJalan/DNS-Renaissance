import io
import sys
import csv
from datetime import datetime

# To make sure all packet types are available
import scapy.all  # noqa
import scapy.packet
from scapy.layers.l2 import Ether
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
            # if i == 300:
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
        if decoded.__class__.__name__ == "Raw":
            payload["class_name"] = "Raw"
            packet["payload"].append(payload)
            continue
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
    return packet


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
                    "TTFB": 0,
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
                            packet["timestamp"] - results[domain]["last_packet_time"]
                        )
                    if results[domain]["TTFB"] == 0:
                        results[domain]["TTFB"] = (
                            packet["timestamp"] - results[domain]["start_time"]
                        )

                    results[domain]["Total Packets"] += 1
                    results[domain]["Total Bytes"] += packet["packet_len"]
                    results[domain]["Total Time"] += (
                        packet["timestamp"] - results[domain]["last_packet_time"]
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
    ]

    # Write the CSV file
    with open(output_file, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for domain, data in results.items():
            row = {
                "Domain": domain,
                "Total Packets": data["Total Packets"],
                "Total Bytes": data["Total Bytes"],
                "Total DNS Packets": data["Total DNS Packets"],
                "Total DNS Bytes": data["Total DNS Bytes"],
                "Total Time": data["Total Time"],
                "Total DNS Time": data["Total DNS Time"],
                "TTFB": data["TTFB"],
            }
            writer.writerow(row)


def main():
    if len(sys.argv) < 2:
        print("Usage: python pcapng-analyzer.py <pcapng_file>")
        sys.exit(1)
    pcapng_file = sys.argv[1]
    output_file = "results.csv"  # Change output file to CSV format
    packets = []
    with open(pcapng_file, "rb") as fp:
        scanner = pcapng.FileScanner(fp)
        packets = get_packets(scanner)

    print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")
    print("EXTRACTION COMPLETE")
    print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")
    results = analyze_packets(packets)
    print("ANALYSIS COMPLETE")
    print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")

    # Save the results to a CSV file instead of JSON
    save_results_to_csv(results, output_file)
    print(f"RESULTS SAVED IN {output_file}")
    print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>")

    # Print the results from the CSV for verification
    # with open(output_file, "r") as csvfile:
    #     reader = csv.reader(csvfile)
    #     for row in reader:
    #         print(", ".join(row))


if __name__ == "__main__":
    main()
