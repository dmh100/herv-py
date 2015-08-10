__author__ = 'Panagiotis Koukos'

import subprocess
import sys
from multiprocessing import cpu_count


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-db',
                        '--blast_database_dir',
                        type=str,
                        required=True,
                        help='This is the directory where the Blast database is located.')
    parser.add_argument('-seq',
                        '--fasta_input_file',
                        type=str,
                        required=True,
                        help='This is the file that contains the sequences to be run through BLASTN.')
    parser.add_argument('-o',
                        '--output_file',
                        type=str,
                        required=False,
                        help='The name of the file where the results will be printed.')

    args = parser.parse_args()
    database, input_file, output_file = args.blast_database_dir, args.fasta_input_file, args.output_file

    try:
        blast = subprocess.check_output(['which', 'blastn']).rstrip()
    except subprocess.CalledProcessError:
        sys.exit('No blastn binary in the system path. Aborting.')

    if not output_file:
        output_file = 'blast.out'

    n_cpu = cpu_count()
    if n_cpu > 4:
        n_cpu = 4

    try:
        subprocess.check_call([blast,
                               '-db', database,
                               '-query', input_file,
                               '-out', output_file,
                               '-outfmt', '6',  # TSV output for easier parsing.
                               '-num_threads', str(n_cpu)])  # parallelise it if possible.
    except subprocess.CalledProcessError:
        sys.exit('Call to blastn failed. Please investigate.')

if __name__ == '__main__':
    main()
