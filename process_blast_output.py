__author__ = 'Panagiotis Koukos'

"""
This module processes the blast output in order to extract the useful
information and store it in an easily accessible format.
"""


def load_repeating_regions(rep_file_name):
    import json
    with open(rep_file_name) as in_file:
        repeating_regions = json.load(in_file)
    return repeating_regions


def format_blast_output_in_dict(blast_output):
    if not isinstance(blast_output, list):
        raise TypeError('The function format_blast_output_in_dict only accepts lists as input.')

    output_dict = {
        'query_id': blast_output[0],
        'chromosome': blast_output[1],
        'percent_id': blast_output[2],
        'alignment_length': blast_output[3],
        'mismatches': blast_output[4],
        'gap_opens': blast_output[5],
        'query_start': blast_output[6],
        'query_end': blast_output[7],
        'subject_start': blast_output[8],
        'subject_end': blast_output[9],
        'evalue': blast_output[10],
        'bitscore': blast_output[11],
    }

    return output_dict


def process_blast_output(file_name):
    import csv
    blast_output = []
    with open(file_name) as in_file:
        lines = csv.reader(in_file, delimiter='\t')
        for line in lines:
            formatted_output = format_blast_output_in_dict(line)
            blast_output.append(formatted_output)
    return blast_output


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-blast',
                        '--blast_input_file',
                        type=str,
                        required=True,
                        help='Input file. Must be in tsv format.')
    parser.add_argument('-repeats',
                        '--repeats_input_file',
                        type=str,
                        required=True,
                        help='Input file. Must be in JSON format.')

    args = parser.parse_args()
    input_file, repeats_file = args.blast_input_file, args.repeats_input_file

    blast_hits = process_blast_output(input_file)
    repeats = load_repeating_regions(repeats_file)

    for i in blast_hits:
        print i

if __name__ == '__main__':
    main()
