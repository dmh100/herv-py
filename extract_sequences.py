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

    # If fasta/json directories are ot defined use the current working directories.
    if not fasta_dir:
        fasta_dir = '.'

    if not json_dir:
        json_dir = '.'

    from pipeline import process_dir
    fasta_files = process_dir(fasta_dir)
    json_files = load_json(json_dir)
    if not len(fasta_files) or not len(json_files):
        from sys import exit
        exit('Looks like the directory does not contain any fasta/json files. Aborting.')

    for json_file in json_files:
        print json_file, json_file.keys()
    for fasta_file in fasta_files:
        print fasta_file

if __name__ == '__main__':
    main()
