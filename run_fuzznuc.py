__author__ = 'Panagiotis Koukos'

"""
fuzznuc.py - Scan input files with fuzznuc.

This module scans the input files for the presence of the specified
nucleotide sequence and stores the results in an aptly named text file.

:param -i, --in: Path to the file which contains the sequences to parse.
:type -i, --in: str or unicode
:param -p, --pat: Pattern to look for. Can only contain A, G, C or T.
:type -p, --pat: str or unicode
:param -o, --out: What file to write the results in.
:type -o, --out: str or unicode
:return None
"""

import subprocess
import sys
import atexit

# From http://stackoverflow.com/a/11270665
try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


# TODO fix the repeating devnull import. Maybe use an exit function?
@atexit.register
def custom_exit():
    DEVNULL.close()


def check_fuzznuc():
    """
    Check for the presence of fuzznuc in the local system.

    This functions uses the linux built in command 'which' to
    check if the command fuzznuc is available.

    :param : none
    :return: The absolute path to the fuzznuc program as returned
             by which on success, None on failure.
    """

    try:
        # stdout=DEVNULL suppresses the output of the system call.
        # TODO Port this through python instead of which for compatibility?
        subprocess.check_call(['which', 'fuzznuc'], stdout=DEVNULL)
    except subprocess.CalledProcessError:
        print 'Unable to locate fuzznuc on the local system. Aborting.'
        custom_exit()
        return None

    fuzznuc = subprocess.check_output(['which', 'fuzznuc']).rstrip()
    return fuzznuc


def call_fuzznuc(fuzznuc, input_file, output_file, pattern, nof_mismatches):
    """
    Call fuzznuc with the specified arguments.

    :param fuzznuc: Full path to the fuzznuc binary, as found by check_fuzznuc.
    :type fuzznuc: str or unicode
    :param input_file: Path to the sequence (FASTA) file.
    :type input_file: str or unicode
    :param output_file: File in which fuzznuc will store its output.
    :type output_file: str or unicode
    :param pattern: Path to the file which contains the fuzznuc settings.
    :type pattern: str or unicode
    :return: None
    """

    if 'prime' in pattern:
        if pattern == '5_prime':
            pattern = 'TGTGGGGAAAAGCAAGAGAG'
        elif pattern == '3_prime':
            pattern = 'AGGGGCAACCCACCCCTACA'
        else:
            raise ValueError('Only 3_prime or 5_prime values are acceptable for the pattern.')

    if not output_file:
        # if 'prime' in pattern
        if pattern == 'TGTGGGGAAAAGCAAGAGAG' or '5_prime':
            output_file = input_file.split('.')[0] + '_5_prime' + '.fuzznuc'
        else:
            output_file = input_file.split('.')[0] + '_3_prime' + '.fuzznuc'
            # print output_file

    try:
        subprocess.check_call([fuzznuc,
                               '-sequence', input_file,
                               '-pattern', pattern,
                               '-pmismatch', nof_mismatches,
                               '-outfile', output_file,
                               '-rformat', 'simple'],
                              stdout=DEVNULL,
                              stderr=subprocess.STDOUT)

        return 1
    except subprocess.CalledProcessError:
        print 'One or more files not found. Aborting.'
        custom_exit()
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--input',
                        type=str,
                        required=True,
                        help='Input file. Must be in FASTA format.')

    parser.add_argument('-o',
                        '--output',
                        type=str,
                        required=False,
                        help='Output file. If not specified, the name of the input file with '
                             'the .fuzznuc suffix.')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p_seq',
                       '--pattern_sequence',
                       type=str,
                       dest='pat_seq',
                       help='DNA pattern to look for in the sequences. Only a/A, g/G, c/C, t/T '
                            'characters acceptable. Is a DNA sequence. Mutually exclusive with '
                            '-p_type.')

    group.add_argument('-p_type',
                       '--pattern_type',
                       type=str,
                       dest='pat_type',
                       choices=['5_prime', '3_prime'],
                       help='DNA pattern to look for in the sequences. Only 5_prime or 3_prime '
                            'acceptable. Mutually exclusive with -p_seq.')

    parser.add_argument('-n',
                        '--number_of_mismatches',
                        dest='nmismatch',
                        default='2',
                        type=str,
                        required=False,
                        help='How many mismatches to include in the fuzznuc mismatches. Default is 2.')

    args = parser.parse_args()
    if args.pat_seq:
        pattern = args.pat_seq
    else:
        pattern = args.pat_type

    input_file, output_file, nof_mismatches = args.input, args.output, args.nmismatch

    # TODO: Write a check for the presence of illegal characters in pattern.
    fuzznuc = check_fuzznuc()
    if fuzznuc:
        call_fuzznuc(fuzznuc, input_file, '', pattern, nof_mismatches)
    else:
        sys.exit('Cannot locate fuzznuc binary in the system. Aborting.')


if __name__ == '__main__':
    main()
