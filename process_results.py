__author__ = 'Panagiotis Koukos'

"""
process_results.py - Process the reports produced by run_fuzznuc.py

This module parses the files produced by the script run_fuzznuc.py
and stores the results(location, length, strand, etc...) in text
files.


"""
import re


def parse_report(path_to_file):
    hits = {}
    which_prime = ''

    try:
        which_prime = determine_prime(path_to_file)
    except UserWarning:
        print ('The provided file does not seem to contain the 3 or the 5 prime'
               ' LTR sequence. Aborting.')

    if which_prime == '5_prime':
        pass

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
                hits[current_id] = {}
                hits[current_id]['read_length'] = seq_match.group(3)

            start_match = start_re.search(line)
            if current_id and start_match:
                hits[current_id]['from'] = start_match.group(1)

            end_match = end_re.search(line)
            if current_id and end_match:
                hits[current_id]['to'] = end_match.group(1)

            strand_match = strand_re.search(line)
            if current_id and strand_match:
                hits[current_id]['strand'] = strand_match.group(1)

            mismatch_match = mismatch_re.search(line)
            if current_id and mismatch_match:
                hits[current_id]['mismatch'] = mismatch_match.group(1)

    valid_hits = check_results(hits, which_prime)
    print 'hits'
    for i in hits:
        print i, hits[i]
    print 'valid_hits'
    for i in valid_hits:
        print i, valid_hits[i]

    return valid_hits


def check_results(hits, prime):
    valid_hits = {}
    for hit in hits:
        length = int(hits[hit]['read_length'])
        _from = int(hits[hit]['from'])
        _to = int(hits[hit]['to'])

        # If the results contain hits of the 5-prime LTR then the
        # sequence that has to be extracted is to the left of the
        # input, whereas 3-prime sequence has to be extracted from
        # the right. These numbers are 1-indexed.
        if prime == '5_prime':
            if (_from - 1) < 20:
                # del hits[hit]
                pass
            else:
                valid_hits[hit] = hits[hit]
            # elif (_from - 1) > 50:
            #     # Take only the first 50 elements.
            #     pass
        else:
            if (length - _to) < 20:
                # del hits[hit]
                pass
            else:
                valid_hits[hit] = hits[hit]
            # elif (length - _to) > 50:
            #     # Take only the first 50 elements.
            #     pass
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
    results = parse_report('ERR145618_1_5_prime.fuzznuc')
    for result_key in sorted(results.keys()):
        print result_key, results[result_key]

if __name__ == '__main__':
    main()
