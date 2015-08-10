__author__ = 'Panagiotis Koukos'

"""
This module processes the blast output in order to extract the useful
information and store it in an easily accessible format.
"""

import json
import csv


def load_repeating_regions(rep_file_name):
    with open(rep_file_name) as in_file:
        repeating_regions = json.load(in_file)
    return repeating_regions


def format_blast_output_in_dict(blast_output):
    if not isinstance(blast_output, list):
        raise TypeError('The function format_blast_output_in_dict only accepts lists as input.')

    output_dict = {
        'query_id': blast_output[0],
        'chromosome': 'chr' + blast_output[1],  # So that it matches the RepeatMasker file format.
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
    blast_output = []
    with open(file_name) as in_file:
        lines = csv.reader(in_file, delimiter='\t')
        for line in lines:
            formatted_output = format_blast_output_in_dict(line)
            blast_output.append(formatted_output)
    return blast_output


def hit_in_repeating_region(hit, repeats):
    hit_start, hit_end = [int(x) for x in sorted([hit['subject_start'], hit['subject_end']])]
    for repeat in repeats:
        repeat_start, repeat_end = [int(x) for x in repeat]
        if repeat_start < hit_start < repeat_end:
            return True
        elif repeat_start > hit_end > repeat_end:
            return True
    else:
        return False


def filter_out_hits_in_repeating_regions(repeats_dict, blast_hits):
    # The top level keys for the repeats dictionary are the chromosomes
    # so they can be used to cut down the search space.

    valid_hits = []

    for hit in blast_hits:
        # print json.dumps(hit, indent=2, separators=(',', ':'))
        chromosome = hit['chromosome']
        if chromosome in repeats_dict:
            repeats_for_chromosome = repeats_dict[chromosome]
            if not hit_in_repeating_region(hit, repeats_for_chromosome):
                valid_hits.append(hit)
        else:
            valid_hits.append(hit)

    return valid_hits


def write_valid_hits(hits, output_file='blast_no_repeats.out'):
    with open(output_file, 'w') as out_file:
        for hit in hits:
            json.dump(hit, out_file, indent=2, separators=(',', ':'))


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
    parser.add_argument('-o',
                        '--output_file',
                        type=str,
                        required=False,
                        help='The name of the file where the results will be printed.')

    args = parser.parse_args()
    input_file, output_file, repeats_file = args.blast_input_file, args.output_file, args.repeats_input_file

    blast_hits = process_blast_output(input_file)
    repeats = load_repeating_regions(repeats_file)
    non_repeating_hits = filter_out_hits_in_repeating_regions(repeats, blast_hits)
    # write_valid_hits(non_repeating_hits, output_file)
    print non_repeating_hits

if __name__ == '__main__':
    main()
