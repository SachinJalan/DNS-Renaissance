'''
In this rogram we analyze the 16 bits of Flags field in the DNS header.
'''

import os
import json

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

def analyze_packets2(packets, fin_results):
    '''
    Fields to care about:
    QR
    AA
    TC
    RD
    RA
    Z
    QDCOUNT
    ANCOUNT
    NSCOUNT
    ARCOUNT
    '''
    for packet in packets:
        if packet["payload"][-1]["class_name"] == "DNS":
            if packet["payload"][-1]["an"] != 'None':
                # DNS RESPONSE
                # we have recieved the DNS response.
                # now we need to analyze the payload and focus on the DNS feilds:
                list_of_dicts_of_layers = list(packet["payload"])
                fields = ["qr", "aa", "tc", "rd", "ra", "z", "qdcount", "ancount", "nscount", "arcount"]
                for field in fields:
                    if field in list_of_dicts_of_layers[-1]:
                        try:
                            fin_results["answer"][field][list_of_dicts_of_layers[-1][field]] += 1
                        except KeyError as e:
                            fin_results["answer"][field][list_of_dicts_of_layers[-1][field]] = 1
                    else:
                        print(list_of_dicts_of_layers[-1])

            else:
                # DNS QUERY
                list_of_dicts_of_layers = list(packet["payload"])
                fields = ["qr", "aa", "tc", "rd", "ra", "z", "qdcount", "ancount", "nscount", "arcount"]
                for field in fields:
                    if field in list_of_dicts_of_layers[-1]:
                        try:
                            fin_results["query"][field][list_of_dicts_of_layers[-1][field]] += 1
                        except KeyError as e:
                            fin_results["query"][field][list_of_dicts_of_layers[-1][field]] = 1
                    else:
                        print(list_of_dicts_of_layers[-1])

def save_results_to_json(results, output_file):
    with open(output_file, "w") as jsonfile:
        json.dump(results, jsonfile, indent=4)

def main():
    DIR_PATH1 = "./pcapngs"
    pcangs =  os.listdir(DIR_PATH1)
    fin_results = {"answer":{}, "query":{}}
    for key in ["qr", "aa", "tc", "rd", "ra", "z", "qdcount", "ancount", "nscount", "arcount"]:
        fin_results["answer"][key] = {}
        fin_results["query"][key] = {}
    
    for pcapng_file in pcangs:
        pcapng_file = DIR_PATH1 + f"/{pcapng_file}"
        domain = os.path.basename(pcapng_file)[:-7]
        # if domain != "amazonaws.com":
        #     continue
        packets = []
        with open(pcapng_file, "rb") as fp:
            scanner = pcapng.FileScanner(fp)
            packets = get_packets(scanner)
        _ = analyze_packets2(packets, fin_results=fin_results)
        # break

    DIR_PATH2 = "./pcapngs2"
    pcangs =  os.listdir(DIR_PATH2)
    for pcapng_file in pcangs:
        pcapng_file = DIR_PATH2 + f"/{pcapng_file}"
        domain = os.path.basename(pcapng_file)[:-7]
        # if domain != "amazonaws.com":
        #     continue
        packets = []
        with open(pcapng_file, "rb") as fp:
            scanner = pcapng.FileScanner(fp)
            packets = get_packets(scanner)
        _ = analyze_packets2(packets, fin_results=fin_results)
    # # remove those domains that don't have any answers
    # fin_results_copy = fin_results.copy()

    # for key in list(fin_results["answer"].keys()):
    #     for key2 in list(fin_results["answer"][key].keys()):  
    #         if fin_results["answer"][key][key2] == []:
    #             del fin_results_copy["answer"][key][key2]

    # for key in list(fin_results["question"].keys()):
    #     for key2 in list(fin_results["question"][key].keys()):
    #         if fin_results["question"][key][key2] == []:
    #             del fin_results_copy["question"][key][key2]


    save_results_to_json(fin_results, "dns-bits.json")
if __name__ == "__main__":
    main()
