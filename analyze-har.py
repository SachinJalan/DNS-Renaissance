import json
import os

def analyze_har(file_path):
    with open(file_path, 'r') as f:
        har_data = json.load(f)

    entries = har_data['log']['entries']

    total_dns_time = 0
    total_wait_time = 0
    total_entries = len(entries)
    dns_requests = 0
    total_time = 0

    for entry in entries:
        timings = entry['timings']
        dns_time = timings.get('dns', -1)
        wait_time = timings.get('wait', 0)

        if dns_time > 0:
            total_dns_time += dns_time
            dns_requests += 1

        total_wait_time += wait_time

    average_dns_time = total_dns_time / dns_requests if dns_requests > 0 else 0
    ratio_dns_packets = dns_requests / total_entries if total_entries > 0 else 0
    average_ttfb = total_wait_time / total_entries if total_entries > 0 else 0
    total_time = total_dns_time + total_wait_time
    # total_time = sum([entry['time'] for entry in entries])

    # print(f"Total Requests: {total_entries}")
    # print(f"Total DNS Requests: {dns_requests}")
    # print(f"Average DNS Resolution Time: {average_dns_time:.2f} ms")
    # print(f"Average Time to First Byte (TTFB): {average_ttfb:.2f} ms")
    # print(f"Ratio of DNS Packets: {ratio_dns_packets:.2f}")

    return total_entries, dns_requests, average_dns_time, average_ttfb, ratio_dns_packets, total_time

# Example Usage
# file_path = 'trace-net.har'
# analyze_har(file_path)

traces_path = 'traces/'
files = os.listdir(traces_path)

# markdown table output
print("| Domain | Total Requests | DNS Requests | Average DNS Time | Average TTFB | Ratio DNS Packets | Total Time |")
print("| --- | --- | --- | --- | --- | --- | --- |")
for file in files:
    if file.endswith('.har'):
        file_path = os.path.join(traces_path, file)
        domain = file.replace('.har', '')
        total_entries, dns_requests, average_dns_time, average_ttfb, ratio_dns_packets, total_time = analyze_har(file_path)
        print(f"| {domain} | {total_entries} | {dns_requests} | {average_dns_time:.2f} | {average_ttfb:.2f} | {ratio_dns_packets:.2f} | {total_time:.2f} |")
