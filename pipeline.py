__author__ = 'Panagiotis Koukos'

"""
This script automates the procedure by putting all of the necessary steps
for the analysis in one place. It imports/launches the other scripts of the
pipeline and executing them with their default options.

"""
import os


def process_dir(path_to_dir, file_suffix):
    files_in_dir = os.listdir(path_to_dir)
    _files = [x for x in files_in_dir if x.endswith(file_suffix)]
    return _files


def main():
    import argparse
    from subprocess import call
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
            list_of_fasta_files = process_dir(abs_path, 'FASTA')
            list_of_fasta_files = [abs_path + '/' + x for x in list_of_fasta_files]
            for fasta_file in list_of_fasta_files:
                for prime in ['5_prime', '3_prime']:
                    print fasta_file, prime
                    # What i want ot do here is:
                    # 1. More helpful print statement. Possibly a % as file size ratio / total.
                    # 2. add the subprocess.CalledProcessError to the except maybe
                    # 3. separate the three stages(run fuzznuc, check results, extract) in three
                    #    functions
                    try:
                        rf.call_fuzznuc(fuzznuc, fasta_file, '', prime, '2')
                    except ValueError:
                        print 'Something is very wrong.'

            list_of_fuzznuc_files = process_dir('.', 'fuzznuc')
            for fuzznuc_file in list_of_fuzznuc_files:
                results = pr.parse_report(fuzznuc_file)
                pr.write_json(results)

            call(['python',
                  'extract_sequences.py',
                  '-fasta',
                  # TODO: SOrt out the final slash, and the paths in general.
                  abs_path + '/'])
        else:
            raise OSError('The provided path does not seem to point to a directory. Aborting.\n')
    else:
        print 'Failed to locate fuzznuc binary in the system path. Aborting.'


if __name__ == '__main__':
    main()
