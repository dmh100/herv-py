__author__ = 'Panagiotis Koukos'

"""
This script process the table output from the UCSC browser in order
to dump the repeated regions in JSON format.
"""


def main():
    import csv
    import json
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--input',
                        type=str,
                        required=True,
                        help='Input file. Must be in tsv format.')
    parser.add_argument('-o',
                        '--output',
                        type=str,
                        required=False,
                        help='Output file. If not present same as the input '
                             'but with a different suffix.')

    args = parser.parse_args()
    input_file, output_file = args.input, args.output

    results = {}

    with open(input_file) as in_file:
        in_file.next()  # The first line is the header.
        lines = csv.reader(in_file, delimiter='\t')
        for words in lines:
            chromosome, genome_start, genome_end = words[5], words[6], words[7]
            if chromosome not in results:
                results[chromosome] = []
            results[chromosome].append([genome_start, genome_end])

    # Sort the list under every chromosome based on the start region
    # of the hit. This allows for binary lookup of the results.
    for result in results:
        results[result].sort(key=lambda x: int(x[0]))

    if not output_file:
        output_file = 'repeating_regions.out'

    with open(output_file, 'w') as out_file:
        json.dump(results, out_file, indent=2, separators=(',', ':'))

if __name__ == '__main__':
    main()
