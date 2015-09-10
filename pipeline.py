__author__ = 'Panagiotis Koukos'

"""
This script automates the procedure by putting all of the necessary steps
for the analysis in one place. It imports/launches the other scripts of the
pipeline and executing them with their default options.

"""
import sys
import herv_lib
import run_fuzznuc
import subprocess
import process_results
import create_fasta_from_json
import extract_sequences
import process_blast_output


def main():
    import argparse

    fuzznuc = herv_lib.Executable('fuzznuc')

    if not fuzznuc:
        sys.exit('Failed to locate fuzznuc binary in the system path. Aborting.')

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
    if not list_of_fasta_files:
        sys.exit('No *.FASTA files found in the specified folder. Aborting.')

    # First parse the file with fuzznuc looking for the 5prime sequence and
    # then for the 3prime. Keep the loop structure like this because of disk
    # buffering.
    for fasta_file in list_of_fasta_files:
        for ltr_seq in ['TGTGGGGAAAAGCAAGAGAG', 'AGGGGCAACCCACCCCTACA']:
            run_fuzznuc.call_fuzznuc(fuzznuc.path,  # Path to the executable
                                     fasta_file,    # Input file
                                     '',            # Output file-name
                                     ltr_seq,       # 3 or 5 prime
                                     '2',)          # Number of mismatches

    # Update the contents of the directory after fuzznuc is done so that the
    # fuzznuc files are added to the contents attribute.
    curr_dir.set_dir_contents()

    list_of_fuzznuc_files = curr_dir.get_files_with_suffix('fuzznuc')
    if not list_of_fuzznuc_files:
        sys.exit('No *.fuzznuc files found in the specified folder. Aborting.')

    for fuzznuc_file in list_of_fuzznuc_files:
        results = process_results.parse_report(fuzznuc_file)
        process_results.write_json(results)

    subprocess.call(['python',
                     'extract_sequences.py',
                     '-fasta',
                     in_dir.path])

    # Create the extract_sequences.fa file.
    curr_dir.set_dir_contents()
    list_of_json_files = curr_dir.get_files_with_suffix('json')
    if not list_of_json_files:
        sys.exit('No json files found in the specified directory. Aborting.')

    json_files = extract_sequences.load_json(list_of_json_files)
    processed_json = create_fasta_from_json.extract_from_json(json_files)
    create_fasta_from_json.write_to_file(processed_json)

    # Run blast.
    subprocess.call([
        'python', 'run_blast.py',
        '-db', '/scratch/pk3414/Homo_sapiens.GRCh38.dna.toplevel.fa',
        '-seq', 'extracted_sequences.fa'
    ])

    # Process the repetitive regions file and store it in JSON. Requires the
    # file with the RepeatMasker regions in TSV format. Only run this the first
    # time you obtain the repeat regions file from UCSC.
    # subprocess.call([
    #     'python', 'extract_repeating_regions.py',
    #     '-i', 'repeating_regions'
    # ])

    # Filter out the blast hits in the repetitive regions. Requires the file
    # from the previous step in JSON format.
    repeats = process_blast_output.load_repeating_regions('repeating_regions.out')
    process_blast_output.process_blast_output('blast.out', repeats)


if __name__ == '__main__':
    main()
