import os
import csv
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate server configuration files." \
    "For each domain that is given in the domain.txt file, a server configuration file is created with the name <domain>-server.conf ")
    parser.add_argument("-d", help="domain.txt file")
    parser.add_argument("-s", help="source directory with the dnsrecon results")
    parser.add_argument("-on", help="output directory to store all the ndn dns server conf files")
    parser.add_argument("-oh", help="output directory to store all the hierarchial dns server conf files")
    # parser.add_argument("-h", help="show this help message and exit", action="help")
    args = parser.parse_args()

    domain_txt = args.d
    source = args.s
    ndn_output_dir = args.on
    hierarchical_output_dir = args.oh
    if not domain_txt or not source or not ndn_output_dir:
        print("Please provide all required arguments: -d, -s, -on, -oh")
        exit(1)
    
    os.makedirs(ndn_output_dir, exist_ok=True)

    with open(domain_txt, "r") as file:
        domains = [line.strip() for line in file.readlines()]
        for domain in domains:
            # read csv files in dnsrecon results directory.
            csv_file = os.path.join(source, f"{domain}.csv")
            if not os.path.exists(csv_file):
                print(f"CSV file for {domain} not found in {source}.")
                continue
            content = [] # Available chard : alpha, nums, :/+._-%
            with open(csv_file, "r") as csvfile:
                '''
                Headers:
                Domain,Type,Name,Address,Target,Port,String
                '''
                reader = csv.reader(csvfile)
                # Skip the header
                next(reader)
                for row in reader:
                    domain = row[0]
                    rtype = row[1]
                    name = row[2]
                    address = row[3]
                    content.append(f"{domain}-{rtype}-{name}-{address}")
            content_str = "+".join(content)

            if domain[-1] != ".":
                domain += "."
            conf_file = os.path.join(ndn_output_dir, f"{domain}-server.conf")
            with open(conf_file, "w") as conf:
                conf.write(f"Name={'/'.join(domain.split('.')[::-1])}\n")
                conf.write(f"Content={content_str}\n")
                conf.write("FreshnessPeriod=1000\n")
            print(f"Configuration file created for {domain} at {conf_file}")

    os.makedirs(hierarchical_output_dir, exist_ok=True)

    with open(domain_txt, "r") as file:
        domains = [line.strip() for line in file.readlines()]
        for domain in domains:
            # read csv files in dnsrecon results directory.
            csv_file = os.path.join(source, f"{domain}.csv")
            if not os.path.exists(csv_file):
                print(f"CSV file for {domain} not found in {source}.")
                continue
            content = {}
            with open(csv_file, "r") as csvfile:
                '''
                Headers:
                Domain,Type,Name,Address,Target,Port,String
                '''
                reader = csv.reader(csvfile)
                # Skip the header
                next(reader)
                for row in reader:
                    domain = row[0]
                    rtype = row[1]
                    name = row[2]
                    address = row[3]
                    if rtype not in content:
                        content[rtype] = []
                    content[rtype].append(f"{domain}-{rtype}-{name}-{address}")

                if domain[-1] != ".":
                    domain += "."
                conf_file = os.path.join(hierarchical_output_dir, f"{domain}-server.conf")
                with open(conf_file, "w") as conf:
                    for rtype in content:
                            conf.write(f"Name={'/'.join(domain.split('.')[::-1])}/{rtype}\n")
                            conf.write(f"Content={'+'.join(content[rtype])}\n")
                            conf.write("FreshnessPeriod=1\n\n")

                print(f"Configuration file created for {domain} at {conf_file}")


    # print(f"Configuration file created at: {conf_path}")