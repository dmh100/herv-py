__author__ = 'Panagiotis Koukos'

"""
process_results.py - Process the reports produced by run_fuzznuc.py

This module parses the files produced by the script run_fuzznuc.py
and stores the results(location, length, strand, etc...) in text
files.


"""
import re
import copy
import json


def parse_report(path_to_file):
    hits = {}
    which_prime = ''

    try:
        which_prime = determine_prime(path_to_file)
    except UserWarning:
        print ('The provided file does not seem to contain the 3 or the 5 prime'
               ' LTR sequence. Aborting.')

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

            # TODO: SORT OUT THE UGLY STRING CONCATENATIONS
            seq_match = seq_re.search(line)
            if seq_match:
                current_id = seq_match.group(1).split('_')[-1] + '.' + which_prime
                hits[current_id] = {}
                hits[current_id]['read_length'] = seq_match.group(3)
                hits[current_id]['prime'] = which_prime

            start_match = start_re.search(line)
            if current_id and start_match:
                hits[current_id]['LTR_from'] = start_match.group(1)

            end_match = end_re.search(line)
            if current_id and end_match:
                hits[current_id]['LTR_to'] = end_match.group(1)

            strand_match = strand_re.search(line)
            if current_id and strand_match:
                hits[current_id]['strand'] = strand_match.group(1)

            mismatch_match = mismatch_re.search(line)
            if current_id and mismatch_match:
                hits[current_id]['mismatch'] = mismatch_match.group(1)

    valid_hits = check_results(hits, which_prime)
    # Add another level to the json object so that the original FASTA file
    # is included as the top level header.
    # The hierarchy of the object is like this:
    # { <filename>: {
    #     <readid.prime>: {
    #       <info>
    #     }
    #   }
    # }
    #
    fasta_name = path_to_file.split('.')[0]

    results_dict = {
        fasta_name: valid_hits
    }

    return results_dict


def write_json(results_dict):
    from os import listdir
    # Check if there is a json file which contains the top level key.
    # If there is extend that one instead of creating a new one.
    fasta_name = results_dict.keys()[0]
    if fasta_name + '.json' in listdir('.'):
        with open(fasta_name + '.json', 'r+') as in_out_file:
            previous_results_dict = json.load(in_out_file)
            results_dict[fasta_name].update(previous_results_dict[fasta_name])
            in_out_file.seek(0)
            json.dump(results_dict, in_out_file, indent=2, separators=(',', ':'))
            in_out_file.truncate()
    else:
        with open(fasta_name + '.json', 'w') as in_out_file:
            json.dump(results_dict, in_out_file, indent=2, separators=(',', ':'))


def check_results(hits, prime):
    valid_hits = {}
    for hit in hits:
        length = int(hits[hit]['read_length'])
        ltr_from = int(hits[hit]['LTR_from'])
        ltr_to = int(hits[hit]['LTR_to'])
        strand = hits[hit]['strand']

        # If the results contain hits of the 5-prime LTR then the
        # sequence that has to be extracted is to the left of the
        # input, whereas 3-prime sequence has to be extracted from
        # the right. These numbers are 1-indexed.

        # Use the copy module to avoid the valid_hits referencing the original.
        if strand == '+':
            if prime == '5_prime' and (ltr_from - 1) >= 20:
                valid_hits[hit] = copy.copy(hits[hit])
                valid_hits[hit]['seq_to'] = str(ltr_from)
                if (ltr_from - 1) >= 50:
                    # Get 50bp to the left of the LTR point of origin
                    seq_from = ltr_from - 50
                    valid_hits[hit]['seq_from'] = str(seq_from)
                else:
                    valid_hits[hit]['seq_from'] = str(1)
            elif prime == '3_prime' and (length - ltr_to) >= 20:
                valid_hits[hit] = copy.copy(hits[hit])
                valid_hits[hit]['seq_from'] = str(ltr_to)
                if (length - ltr_to) >= 50:
                    # get 50bp to the right of the LTR
                    seq_to = ltr_to + 50
                    valid_hits[hit]['seq_to'] = str(seq_to)
                else:
                    valid_hits[hit]['seq_to'] = str(length)
        else:
            if prime == '5_prime' and (length - ltr_to) >= 20:
                valid_hits[hit] = copy.copy(hits[hit])
                valid_hits[hit]['seq_from'] = str(ltr_to)
                if (length - ltr_to) >= 50:
                    # Get 50bp to the left of the LTR point of origin
                    seq_to = (length - ltr_to) + 50
                    valid_hits[hit]['seq_to'] = str(seq_to)
                else:
                    valid_hits[hit]['seq_to'] = str(length)
            elif prime == '3_prime' and (ltr_from - 1) >= 20:
                valid_hits[hit] = copy.copy(hits[hit])
                valid_hits[hit]['seq_to'] = str(ltr_from)
                if (ltr_from - 1) >= 50:
                    # get 50bp to the right of the LTR
                    seq_from = ltr_from - 50
                    valid_hits[hit]['seq_from'] = str(seq_from)
                else:
                    valid_hits[hit]['seq_from'] = str(1)
    return valid_hits


def determine_prime(path_to_file, pattern=''):
    pattern_re = re.compile(r'#\s*-pattern\s*(\S+)')
    with open(path_to_file) as in_file:
        for line in in_file:
            line = line.rstrip()
            pattern_match = pattern_re.search(line)
            if pattern_match:
                pattern = pattern_match.group(1)
                break
    if pattern == 'AGGGGCAACCCACCCCTACA':
        return '3_prime'
    elif pattern == 'TGTGGGGAAAAGCAAGAGAG':
        return '5_prime'
    else:
        raise UserWarning('The pattern is not the 5 or the 3 prime LTR.')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--input',
                        type=str,
                        required=True,
                        help='Input file. Must be in fuzznuc simple format.')

    args = parser.parse_args()
    input_file = args.input

    results = parse_report(input_file)
    write_json(results)
    # for result_key in sorted(results.keys()):
    #     print result_key, results[result_key]

if __name__ == '__main__':
    main()
