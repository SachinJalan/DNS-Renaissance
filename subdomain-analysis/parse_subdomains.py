import csv

# Read the improperly formatted CSV content
input_file = '/home/mithilpn/Projects/project-course-dns/DNS-Renaissance/iiti_ac_in_subdomains.csv'
output_file = '/home/mithilpn/Projects/project-course-dns/DNS-Renaissance/iiti_ac_in_subdomains_corrected.csv'

with open(input_file, 'r') as infile:
    lines = infile.readlines()

# Parse the content and store it in a list of dictionaries
parsed_data = []
current_row = {}

for line in lines:
    # print(line)
    # count -= 1
    line = line.strip()
    if line.startswith('No'):
        continue  # Skip the header line
    if line.startswith(','):
        continue  # Skip the comma-only lines
    if line:
        # print(line)
        parts = line.split('\t')
        # print(parts)
        if len(parts) == 2:
            current_row = {
                'Subdomain': parts[0].strip(),
                'IP': parts[1].strip(),
            }
            parsed_data.append(current_row)
        # elif len(parts) == 4:
        #     current_row = {
        #         'No': parts[0].strip(),
        #         'Subdomain': parts[1].strip(),
        #         'IP': parts[2].strip(),
        #         'Provider': parts[3].strip()
        #     }
        #     parsed_data.append(current_row)
        # print(current_row)
# Write the parsed data to a correctly formatted CSV file
with open(output_file, 'w', newline='') as csvfile:
    fieldnames = ['Subdomain', 'IP']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in parsed_data:
        writer.writerow(row)

print(f"Correctly formatted CSV file saved to {output_file}")
