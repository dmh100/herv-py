__author__ = 'Panagiotis Koukos'

"""
This script goes through the json files in a dir, processes them
and creates the extracted_sequences.fa file to be fed into BLAST.
"""


def concat_ltr_seq(strand, prime, ltr, seq):
    if strand == '+':
        if prime == '5_prime':
            concatenated = seq + ltr
        else:
            concatenated = ltr + seq
    else:
        if prime == '5_prime':
            concatenated = ltr + seq
        else:
            concatenated = seq + ltr
    return concatenated


def extract_from_json(json_dictionaries):
    processed_json = []
    strand_dict = {
        '+': 'forward',
        '-': 'reverse'
    }

    for json_file in json_dictionaries:
        fasta_file = json_file.keys()[0]
        read_ids = json_file[fasta_file].keys()
        for read_id in read_ids:
            strand = json_file[fasta_file][read_id]['strand']
            prime = json_file[fasta_file][read_id]['prime']
            ltr = json_file[fasta_file][read_id]['LTR_sequence']
            seq = json_file[fasta_file][read_id]['extracted_sequence']

            # Include only the hits which have 50bp flanking them. This is
            # done to reduce the number of hits that make it to the final
            # stages of the analysis, and also because the 52-fold coverage
            # will probably account for it.
            seq_start = int(json_file[fasta_file][read_id]['seq_from'])
            seq_to = int(json_file[fasta_file][read_id]['seq_to'])

            # The len(seq) check is there because some parts of the fasta files
            # have become corrupted/the sequence is not available.
            if seq_to - seq_start == 50 and len(seq):
                my_id = '.'.join([fasta_file, read_id, strand_dict[strand]])
                final_seq = concat_ltr_seq(strand, prime, ltr, seq)

                processed_json.append({
                    'id': my_id,
                    'seq': final_seq
                })
    return processed_json


def write_to_file(json_files):
    with open('extracted_sequences.fa', 'a') as out_file:
        for json_file in json_files:
            out_file.write('>' + json_file['id'] + '\n')
            out_file.write(json_file['seq'] + '\n')


def main():
    from pipeline import process_dir
    from extract_sequences import load_json
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-d',
                        '--input_dir',
                        type=str,
                        required=True,
                        help='Input directory. This is the directory where the json'
                             ' files are located.')

    args = parser.parse_args()
    in_dir = args.input_dir

    json_files = process_dir(in_dir, 'json')
    if len(json_files) < 1:
        from sys import exit
        exit('No json files found in the specified directory. Aborting.')

    json_files = load_json(json_files)
    processed_json = extract_from_json(json_files)
    write_to_file(processed_json)

if __name__ == '__main__':
    main()
