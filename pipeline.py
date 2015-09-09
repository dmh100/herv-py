__author__ = 'Panagiotis Koukos'

"""
This script automates the procedure by putting all of the necessary steps
for the analysis in one place. It imports/launches the other scripts of the
pipeline and executing them with their default options.

"""
import herv_lib
import run_fuzznuc


def call_fuzznuc(fuzznuc, list_of_fasta_files):
    for fasta_file in list_of_fasta_files:
        for prime in ['5_prime', '3_prime']:
            try:
                run_fuzznuc.call_fuzznuc(fuzznuc.path,  # Path to the executable
                                         fasta_file,    # Input file
                                         '',            # Output file-name
                                         prime,         # 3 or 5 prime
                                         '2')           # Number of mismatches
            except ValueError as e:
                print e


def main():
    import argparse
    from subprocess import call
    import process_results as pr
    import create_fasta_from_json as cf
    import extract_sequences as ec
    import process_blast_output as pb

    fuzznuc = herv_lib.Executable('fuzznuc')

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
        in_dir = herv_lib.Directory(in_dir)
        curr_dir = herv_lib.Directory()  # Default is the current directory.

        list_of_fasta_files = in_dir.get_files_with_suffix('FASTA')
        print list_of_fasta_files
        call_fuzznuc(fuzznuc, list_of_fasta_files)

        # Update the contents of the directory after fuzznuc is done.
        curr_dir.set_dir_contents()

        list_of_fuzznuc_files = curr_dir.get_files_with_suffix('fuzznuc')
        print list_of_fuzznuc_files
        for fuzznuc_file in list_of_fuzznuc_files:
            results = pr.parse_report(fuzznuc_file)
            pr.write_json(results)

        call(['python',
              'extract_sequences.py',
              '-fasta',
              in_dir.path])

        # Create the extract_sequences.fa file.
        curr_dir.set_dir_contents()
        list_of_json_files = curr_dir.get_files_with_suffix('json')
        if len(list_of_json_files) < 1:
            from sys import exit
            exit('No json files found in the specified directory. Aborting.')

        json_files = ec.load_json(list_of_json_files)
        processed_json = cf.extract_from_json(json_files)
        cf.write_to_file(processed_json)

        # Run blast.
        # call([
        #     'python', 'run_blast.py',
        #     '-db', '/scratch/pk3414/Homo_sapiens.GRCh38.dna.toplevel.fa',
        #     '-seq', 'extracted_sequences.fa'
        # ])

        # Process the repetitive regions file and store it in JSON. Requires the
        # file with the RepeatMasker regions in TSV format.
        # call([
        #     'python', 'extract_repeating_regions.py',
        #     '-i', 'repeating_regions'
        # ])

        # Filter out the blast hits in the repetitive regions. Requires the file
        # from the previous step in JSON format.
        repeats = pb.load_repeating_regions('repeating_regions.out')
        pb.process_blast_output('sample_blast.out', repeats)
        # pb.write_valid_hits(blast_hits)
    else:
        print 'Failed to locate fuzznuc binary in the system path. Aborting.'


if __name__ == '__main__':
    main()
