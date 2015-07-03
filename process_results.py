__author__ = 'Panagiotis Koukos'

"""
process_results.py - Process the reports produced by run_fuzznuc.py

This module parses the files produced by the script run_fuzznuc.py
and stores the results(location, length, strand, etc...) in text
files.


"""
import re


def parse_report(path_to_file):
    results = {}
    # Define the regular expressions to be used in the parsing of the document.

    seq_re = re.compile(r'# Sequence:\s*(\S+)\s*from: (\S+)\s*to: (\S+)')
    start_re = re.compile(r'^Start: (\S+)')
    end_re = re.compile(r'^End: (\S+)')
    strand_re = re.compile(r'^Strand: (\S+)')
    mismatch_re = re.compile(r'^Mismatch: (\S+)')

    with open(path_to_file) as in_file:
        current_id = False
        for line in in_file:
            line = line.rstrip()

            seq_match = seq_re.search(line)
            if seq_match:
                current_id = seq_match.group(1)
                results[current_id] = {}
                results[current_id]['read_length'] = seq_match.group(3)

            start_match = start_re.search(line)
            if current_id and start_match:
                results[current_id]['from'] = start_match.group(1)

            end_match = end_re.search(line)
            if current_id and end_match:
                results[current_id]['to'] = end_match.group(1)

            strand_match = strand_re.search(line)
            if current_id and strand_match:
                results[current_id]['strand'] = strand_match.group(1)

            mismatch_match = mismatch_re.search(line)
            if current_id and mismatch_match:
                results[current_id]['mismatch'] = mismatch_match.group(1)

    for result_key in sorted(results.keys()):
        print result_key, results[result_key]

    return -2


def check_header():
    pass


def main():
    parse_report('test.fuzznuc')

if __name__ == '__main__':
    main()
