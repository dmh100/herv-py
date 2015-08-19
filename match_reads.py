__author__ = 'Panagiotis Koukos'

"""
This module goes through the BLAST results file and tries to
match a 5_prime read with a 3_prime one. The BLAST file should
have been pre-processed at this stage to remove the hits in
repeating regions of the genome.
"""

import csv
import process_blast_output as pb


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--input',
                        type=str,
                        required=True,
                        help='Input file. Must be in tsv format.')

    pass

if __name__ == "__main__":
    main()
