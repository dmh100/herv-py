__author__ = 'Panagiotis Koukos'

"""
This script automates the procedure by putting all of the necessary steps
for the analysis in one place. It imports/launches the other scripts of the
pipeline and executing them with their default options.

"""
import os


def process_dir(path_to_dir):
    files_in_dir = os.listdir(path_to_dir)
    fasta_files = [x for x in files_in_dir if x.endswith('FASTA')]
    return fasta_files


def main():
    import argparse
    import run_fuzznuc as rf
    import process_results as pr

    fuzznuc = rf.check_fuzznuc()

    if fuzznuc:
        parser = argparse.ArgumentParser()
        parser.add_argument('-d',
                            '--input_dir',
                            type=str,
                            required=True,
                            help='Input directory. This is the directory where the FASTA'
                                 ' files are located.')

        args = parser.parse_args()
        in_dir = args.input_dir

        if os.path.isdir(in_dir):
            abs_path = os.path.abspath(in_dir)
            list_of_fasta_files = process_dir(abs_path)
            for fasta_file in list_of_fasta_files:
                for prime in ['5_prime', '3_prime']:
                    print os.path.abspath(fasta_file), prime
                    try:
                        fuzznuc_status = rf.call_fuzznuc(fuzznuc, fasta_file, '', prime, '2')
                        if fuzznuc_status:
                            pr.parse_report(fuzznuc_status, '')
                    except ValueError:
                        print 'Something is very wrong.'
        else:
            raise OSError('The provided path does not seem to point to a directory. Aborting.\n')
    else:
        print 'Failed to locate fuzznuc binary in the system path. Aborting.'


if __name__ == '__main__':
    main()
