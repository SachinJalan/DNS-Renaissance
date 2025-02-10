# %%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import sys
import os
from scapy.all import rdpcap, DNS, TCP, UDP


# %%
# Load the pcapng file and filter DNS packets
def load_pcapng(file_name):
    packets = rdpcap(file_name)
    dns_packets = []

    for pkt in packets:
        if pkt.haslayer(DNS):
            dns_packets.append(bytes(pkt[DNS]))  # Extract raw DNS data
        # if pkt.haslayer(TCP):
        #     dns_packets.append(bytes(pkt[TCP]))
        # if pkt.haslayer(UDP):
        #     dns_packets.append(bytes(pkt[UDP]))

    return dns_packets


# %%
# Convert each byte in the DNS packet to a bit string
def bytes_to_bits(byte_data):
    bit_string = "".join(f"{byte:08b}" for byte in byte_data)
    return bit_string


# %%
# Analyze DNS packets and extract bit-level data
def analyze_dns_packets(packets):
    # bit_positions = 8 * 512  # Assume max 512 bytes (4096 bits)
    bit_positions = 512
    bit_counts = np.zeros(bit_positions)
    packets_len = len(packets)
    # Iterate through each packet
    for raw_dns_data in packets:
        try:
            bit_string = bytes_to_bits(raw_dns_data)  # Convert bytes to bit string
        except:
            print(f"Error converting bytes to bits  {raw_dns_data}")
            packets_len -= 1
            continue
        for i, bit in enumerate(bit_string):
            if i < bit_positions:  # Avoid overflows for very large packets
                bit_counts[i] += int(bit)  # Count '1's in each bit position

    # return bit_counts, len(packets)
    return bit_counts, packets_len


# %%
# Main function to execute the analysis
# def main():
# file_name = '/home/mithilpn/Projects/project-course-dns/DNS-Renaissance/pcapngs/iitgn.ac.in.pcapng'  # Replace with your pcapng file path
DIR = "./pcapngs"
DIR2 = "./pcapngs2"
packets = []
for file_name in os.listdir(DIR):
    packets += load_pcapng(f"{DIR}/{file_name}")
for file_name in os.listdir(DIR2):
    packets += load_pcapng(f"{DIR2}/{file_name}")

# packets += load_pcapng(file_name)

if not packets:
    print("No DNS packets found in the file.")
    sys.exit(1)

# Analyze DNS packets
bit_counts, num_packets = analyze_dns_packets(packets)
print("Num Packets:", num_packets)
print("Print DNS HEader bit counts:", bit_counts[:97])
# count number of zero bits along with there positions
# print distinct bitcount values
print(f"Distinct bit counts: {np.unique(bit_counts)}")

zero_bits = np.where(bit_counts == 0)
print(f"Number of zero bits: {len(zero_bits[0])}")
print(f"Zero bits positions: {zero_bits[0]}")

# count number of bits that are always 1 along with there positions
one_bits = np.where(bit_counts >= max(bit_counts) - 5)
print(f"Number of one bits: {len(one_bits[0])}")
print(f"One bits positions: {one_bits[0]}")


# %%
# Plot histogram for each bit
def plot_bit_histogram(bit_counts, num_packets):
    bit_positions = len(bit_counts)
    normalized_counts = bit_counts / num_packets  # Normalize counts to percentage

    # plt.figure(figsize=(15, 6))
    # plt.bar(range(bit_positions), normalized_counts, color="blue", width=1)
    # plt.xlabel("Bit Position")
    # plt.ylabel("Probability of Bit Being Set (1)")
    # plt.title("Bit-wise Histogram of DNS Packet Data")
    # plt.savefig("bits-hist.png")
    # plt.show()

    plt.figure(figsize=(12, 8))
    # sns.reset_defaults()
    # sns.set_theme(
    #     context="poster",
    #     font="Calibri",
    #     font_scale=1,
    #     palette="deep",
    #     style="ticks",
    #     rc={"figure.figsize": (12, 8), "lines.linewidth": 0.5},
    # )
    # sns.set(font="Calibri", font_scale=1.2)
    mpl.rcParams["font.family"] = "Open Sans"
    mpl.rcParams["font.size"] = 20
    sns.barplot(x=range(bit_positions), y=normalized_counts)
    plt.xlabel("Bit Position")
    plt.ylabel("Probability of Bit Being Set (1)")
    plt.xticks(range(0, bit_positions, 32))
    plt.title("Bit-wise Histogram of DNS Packet Data")
    plt.savefig("bits-hist.pdf")
    plt.show()


# Plot the bit histogram
plot_bit_histogram(bit_counts, num_packets)


# %%
