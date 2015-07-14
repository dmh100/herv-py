__author__ = 'Panagiotis Koukos'

"""
This module extracts the sequences from the original input files based
on the findings of the previous two scripts in the pipeline.
"""
import json
import os


def load_json(path_to_json_dir):
    json_files = []
    for _file in os.listdir(path_to_json_dir):
        if _file.endswith('json'):
            with open(_file) as in_file:
                json_files.append(json.load(in_file))
    return json_files


def main():
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
    fasta_files = sorted(process_dir(fasta_dir))
    json_files = load_json(json_dir)
    if not len(fasta_files) or not len(json_files):
        from sys import exit
        exit('Looks like the directory does not contain any fasta/json files. Aborting.')

    with open('extracted_sequences.fa', 'a') as out_file:
        for json_file in json_files:
            fasta_file = json_file.keys()[0]
            path_to_fasta_file = fasta_dir + fasta_file + '.FASTA'
            read_ids = json_file[fasta_file].keys()
            for read_id in read_ids:
                extract_from = int(json_file[fasta_file][read_id]['extract_from'])
                extract_to = int(json_file[fasta_file][read_id]['extract_to'])
                prime = json_file[fasta_file][read_id]['prime']
                read_id_grep = '_' + read_id.split('_')[0] + '$'

                # The most efficient way of doing this is probably grep.
                # But maybe a TODO for a benchmark if i have the time
                from subprocess import check_output
                output = check_output(['grep',
                                       '-A1',
                                       read_id_grep,
                                       path_to_fasta_file])
                sequence = output.split('\n')[1]
                # print fasta_file, read_id, extract_from, extract_to
                # print sequence
                if prime == '5_prime':
                    extracted_sequence = sequence[extract_from - 1:extract_to - 1]
                    # print ' ' * (extract_from - 1) + extracted_sequence
                else:
                    extracted_sequence = sequence[extract_from:extract_to]
                    # print ' ' * extract_from + extracted_sequence

                out_file.write('>' + fasta_file + '_' + read_id + '\n')
                out_file.write(extracted_sequence + '\n')

if __name__ == '__main__':
    main()
