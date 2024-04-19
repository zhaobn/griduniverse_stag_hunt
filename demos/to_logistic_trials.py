import argparse
import os
import csv

def examine_csv_file(file_path, output_file):
    print("Here")
    with open(file_path, 'r', newline='') as csvfile:
        print("reading file")
        reader = csv.reader(csvfile)
        output_file.write("dyad,visible,chat,stag, trial")
        output_file.write("\n")
        
        output = [0, 0, 0, 0, 0]
        for row in reader:
            for i in range(3, 8):
                output[0:3] = row[0:3]
                output[3] = row[i]
                output[4] = i - 3
                output_file.write(','.join(map(str, output)) + '\n')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process CSV files in a directory.')
    parser.add_argument('file_path', help='The file')
    parser.add_argument('output_file', help='Output file name')

    args = parser.parse_args()

    filepath = args.file_path
    output_file_path = args.output_file

    print("Here")


    # Open the output file for writing
    with open(output_file_path, 'w') as output_file:
        # Iterate over each CSV file
        examine_csv_file(filepath, output_file)