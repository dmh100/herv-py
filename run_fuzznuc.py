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


def call_fuzznuc(fuzznuc, input_file, output_file, pattern, nof_mismatches, complement=True):
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

    if pattern != 'TGTGGGGAAAAGCAAGAGAG' and pattern != 'AGGGGCAACCCACCCCTACA':
        raise RuntimeWarning('Sequence other than the 3prime or 5prime LTR consensus of the'
                             'HERV-K113 pro-virus detected. Proceeding at your own risk.')

    if not output_file:
        if pattern == 'TGTGGGGAAAAGCAAGAGAG':
            output_file = os.path.basename(input_file).split('.')[0] + '.5_prime' + '.fuzznuc'
        else:
            output_file = os.path.basename(input_file).split('.')[0] + '.3_prime' + '.fuzznuc'

    try:
        fuzznuc_arguments = [
            fuzznuc,
            '-sequence', input_file,
            '-pattern', pattern,
            '-pmismatch', nof_mismatches,
            '-outfile', output_file,
            '-rformat', 'simple'
        ]

        if complement:
            fuzznuc_arguments.append('-complement')

        subprocess.check_call(fuzznuc_arguments,
                              stdout=DEVNULL,
                              stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print 'Error during the execution of fuzznuc. Error returned was:', e
        custom_exit()


def main():
    import argparse
    import herv_lib

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

    parser.add_argument('-p',
                        '--pattern',
                        type=str,
                        required=True,
                        help='DNA pattern to look for in the sequences. Only a/A, g/G, c/C, t/T '
                             'characters acceptable. Is a DNA sequence.')

    parser.add_argument('-n',
                        '--number_of_mismatches',
                        dest='nmismatch',
                        default='2',
                        type=str,
                        required=False,
                        help='How many mismatches to include in the fuzznuc mismatches. Default is 2.')

    parser.add_argument('-c',
                        '--complement',
                        default='Y',
                        choices=['Y', 'N'],
                        type=str,
                        required=False,
                        help='Y means that fuzznuc will also reverse compliment the specified pattern '
                             'and look for it in the other strand. Default is Y.')

    args = parser.parse_args()

    complement = True if args.complement == 'Y' else False
    input_file, output_file, nof_mismatches, pattern = args.input, args.output, args.nmismatch, args.pattern

    fuzznuc = herv_lib.Executable('fuzznuc')
    if fuzznuc:
        try:
            call_fuzznuc(fuzznuc.path, input_file, '', pattern, nof_mismatches, complement)
        except ValueError as e:
            # Given the restriction on 5_prime/3_prime above this exception should never be raised,
            # If the sequences are the HERV-K consensus sequences.
            print ('The specified pattern does not conform to the 3 or 5 prime consensus sequences',
                   'for HERV-K113. Unless you are using sequences with different origin, something',
                   'is wrong. Please investigate. Error returned was:', e)
    else:
        sys.exit('Cannot locate fuzznuc binary in the system. Aborting.')


if __name__ == '__main__':
    main()
