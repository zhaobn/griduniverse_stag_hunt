import argparse
import csv
import os
import json

def examine_csv_file(file_path, output_file, i):
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        # Skip the first line
        next(reader)
        
        output = [i, 0, 0, 0, 0, 0, 0, 0]
        conditions_checked = False
        round_number = 0
        stag_collected = 0

        for row in reader:
            if round_number < 5:

                # Handle line not long enough
                if len(row) < 11:
                    print("File messed up")
                    print(file_path)
                    return

                data = row[10].strip('"')

                
                # Handle empty or malformed JSON data
                if not data:
                    continue
                
                try:
                    json_data = json.loads(data)
                except json.JSONDecodeError:
                    # Skip processing the current row
                    continue

                if not conditions_checked:
                    if "others_visible" in json_data:
                        if json_data.get("others_visible") == True:
                            output[1] = 1
                        if json_data.get("chat_visible") == True:
                            output[2] = 1
                        conditions_checked = True

                if "type" in json_data:
                    event_type = json_data.get("type")
                    if event_type == "round_end":
                        round_number += 1
                        output[round_number + 2] = stag_collected
                        stag_collected = 0

                    if event_type == "item_transition_info":
                        item_id = json_data["item"]["item_id"]
                        if item_id == "stag":
                            stag_collected = 1

        output_file.write(','.join(map(str, output)) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process CSV files in a directory.')
    parser.add_argument('directory', help='Directory containing CSV files')
    parser.add_argument('output_file', help='Output file name')

    args = parser.parse_args()

    directory_path = args.directory
    output_file_path = args.output_file

    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]

    # Open the output file for writing
    with open(output_file_path, 'w') as output_file:
        # Iterate over each CSV file
        i = 0
        for csv_file in csv_files:
            csv_file_path = os.path.join(directory_path, csv_file)
            examine_csv_file(csv_file_path, output_file, i)
            i += 1
