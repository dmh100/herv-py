__author__ = 'Panagiotis Koukos'

"""
This module extracts the sequences from the original input files based
on the findings of the previous two scripts in the pipeline.
"""
import json
import os


def load_json(json_files):
    json_dicts = []
    for json_file in json_files:
        with open(json_file) as in_file:
            json_dicts.append(json.load(in_file))
    return json_dicts


def sort_read_ids(read_ids_and_primes):
    primes = {}
    read_ids = []
    for i in read_ids_and_primes:
        read_id, prime = i.split('.')
        read_ids.append(read_id)
        primes[read_id] = prime

    sorted_read_ids = sorted(read_ids, key=int)
    for index, read_id in enumerate(sorted_read_ids):
        sorted_read_ids[index] = read_id + '.' + primes[read_id]
    return sorted_read_ids


def main():
    import re
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-fasta',
                        '--fasta_input_dir',
                        type=str,
                        required=False,
                        help='Input directory. This is the directory where the FASTA'
                             ' files are located. Defaults to the current working directory.')
    parser.add_argument('-json',
                        '--json_input_dir',
                        type=str,
                        required=False,
                        help='Input directory. This is the directory where the JSON'
                             ' files are located. Defaults to the current working directory.')

    args = parser.parse_args()
    fasta_dir, json_dir = args.fasta_input_dir, args.json_input_dir

    # If fasta/json directories are not defined use the current working directories.
    if not fasta_dir:
        fasta_dir = '.'

    if not json_dir:
        json_dir = '.'

    from pipeline import process_dir
    fasta_files = sorted(process_dir(fasta_dir, 'FASTA'))
    json_files = process_dir(json_dir, 'json')
    if not len(fasta_files) or not len(json_files):
        from sys import exit
        exit('Looks like the directory does not contain any fasta/json files. Aborting.')

    json_files = load_json(json_files)
    # print json.dumps(json_files, indent=2, separators=(',', ':'))

    with open('extracted_sequences.fa', 'a') as out_file:
        for json_file in json_files:
            fasta_file = json_file.keys()[0]
            path_to_fasta_file = fasta_dir + fasta_file + '.FASTA'
            read_ids = json_file[fasta_file].keys()
            sorted_read_ids = sort_read_ids(read_ids)
            with open(path_to_fasta_file) as in_file:
                for read_id in sorted_read_ids:
                    extract_from = int(json_file[fasta_file][read_id]['extract_from'])
                    extract_to = int(json_file[fasta_file][read_id]['extract_to'])
                    prime = json_file[fasta_file][read_id]['prime']
                    read_id_test = read_id.split('.')[0]

                    sequence = None
                    read_id_re = re.compile(r'_(\d+)$')
                    for line in in_file:
                        if line.startswith('>'):
                            read_id_match = read_id_re.search(line)
                            if read_id_match:
                                read_id_extracted = read_id_match.group(1)
                                if read_id_extracted == read_id_test:
                                    sequence = next(in_file)
                                    break
                    if sequence:
                        if prime == '5_prime':
                            extracted_sequence = sequence[extract_from - 1:extract_to - 1]
                            # print ' ' * (extract_from - 1) + extracted_sequence
                        else:
                            extracted_sequence = sequence[extract_from:extract_to]
                            # print ' ' * extract_from + extracted_sequence

                        out_file.write('>' + fasta_file + '.' + read_id + '\n')
                        out_file.write(extracted_sequence + '\n')

if __name__ == '__main__':
    main()
