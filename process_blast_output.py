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

    if len(blast_output[1]) <= 2:
        # So that it matches the RepeatMasker file format
        # and it only catches chromosomes 1-22, X, Y.
        output_dict['chromosome'] = 'chr' + blast_output[1]
    else:
        output_dict['chromosome'] = blast_output[1]

    return output_dict


def binary_search_of_repeats(regions_list, hit):
    if len(regions_list) == 0:
        return False
    list_len = len(regions_list)
    hit_start, hit_end = [int(x) for x in sorted([hit['subject_start'], hit['subject_end']])]
    index = list_len // 2
    repeat_start, repeat_end = [int(x) for x in regions_list[index]]
    if hit_in_repeating_region(hit_start, hit_end, repeat_start, repeat_end):
        return True
    else:
        if hit_start > repeat_start:
            return binary_search_of_repeats(regions_list[index + 1:], hit)
        else:
            return binary_search_of_repeats(regions_list[:index], hit)


def non_recursive_binary_search_of_repeats(regions_list, hit):
    found = False
    start, end = 0, len(regions_list) - 1
    hit_start, hit_end = [int(x) for x in sorted([hit['subject_start'], hit['subject_end']])]

    while start <= end and not found:
        index = (start + end) // 2
        repeat_start, repeat_end = [int(x) for x in regions_list[index]]
        if hit_in_repeating_region(hit_start, hit_end, repeat_start, repeat_end):
            found = True
        else:
            if hit_start > repeat_start:
                start = index + 1
            else:
                end = index - 1

    return found


def filter_by_query_length(prime, strand, start, end):
    if (strand == 'forward' and prime == '5_prime') or (strand == 'reverse' and prime == '3_prime'):
        if start == 1 and end == 50:
            return True
        else:
            return False
    elif (strand == 'reverse' and prime == '5_prime') or (strand == 'forward' and prime == '3_prime'):
        if start == 21 and end == 70:
            return True
        else:
            return False
    else:
        raise RuntimeError('Unexpected combination of strand and prime.')


def process_blast_output(file_name, repeats):
    # Decrease the writing frequency.
    with open(file_name) as in_file, open('blast_no_repeats.out', 'w') as out_file:
        lines = csv.reader(in_file, delimiter='\t')
        processed_blast_output = []
        for line in lines:
            formatted_output = format_blast_output_in_dict(line)
            chromosome = formatted_output['chromosome']

            # Parse the query id in order to extract strand and prime
            query_id = formatted_output['query_id']
            query_id = query_id.split('.')
            prime, strand = query_id[2:]

            # Get only the hits that have fully matched the flanking sequence
            q_start = int(formatted_output['query_start'])
            q_end = int(formatted_output['query_end'])

            try:
                if filter_by_query_length(prime, strand, q_start, q_end):
                    if chromosome in repeats:
                        repeats_for_chromosome = repeats[chromosome]
                        if not non_recursive_binary_search_of_repeats(repeats_for_chromosome, formatted_output):
                            processed_blast_output.append('\t'.join(line))
                    else:
                        processed_blast_output.append('\t'.join(line))
            except RuntimeError as e:
                print ' ', e, 'Query id is', '.'.join(query_id)

            if len(processed_blast_output) == 1000:
                write_valid_hits(processed_blast_output, out_file)
                processed_blast_output = []
        if len(processed_blast_output):
            write_valid_hits(processed_blast_output, out_file)


def hit_in_repeating_region(hit_start, hit_end, repeat_start, repeat_end):
    if repeat_start < hit_start < repeat_end:
        return True
    elif repeat_start > hit_end > repeat_end:
        return True
    else:
        return False


def write_valid_hits(hits, out_file):
    for hit in hits:
        out_file.write(hit + '\n')


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

    repeats = load_repeating_regions(repeats_file)
    process_blast_output(input_file, repeats)

if __name__ == '__main__':
    main()
