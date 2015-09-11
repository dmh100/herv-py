# herv-py
A python pipeline for the detection of HERV-K elements in modern and ancient Hominid genomes.

# Before first run

The external dependencies of the pipeline are:

1. The `blastn` program, part of the BLAST suite (ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/).
2. The `makeblastdb` program, part of the same suite.
3. The `fuzznuc` program, available through the EMBOSS suite (ftp://emboss.open-bio.org/pub/EMBOSS/).
4. A file which contains the regions of the human genome which
have been determined as repetitive by [RepeatMasker](http://www.repeatmasker.org/RMDownload.html). This file
can be obtained from the [UCSC table browser interface](https://genome.ucsc.edu/cgi-bin/hgTables).
5. The human genome in FASTA format. Available from ftp://ftp.ensembl.org/pub/release-81/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.toplevel.fa.gz .
6. The ancient hominid genome you want to analyse.

# The pipeline

It is recommended to use this pipeline from the file `pipeline.py` which
contains the default options as I determined them during its development.
The dataset I used during the development was the Denisovan genome.

## 1. Locating the LTR sequences

This is done with the program `fuzznuc` which is controlled by the script `run_fuzznuc.py`.
If other sequences than the HERV-K113 consensus LTR sequences are provided as templates
it will throw an error, but this setting is easy to bypass. Beware of breaking downstream
compatibility however, since which is the 5 and which is the 3 prime LTR is determined by the 
sequence itself. If the program does not recognise either sequence the latter steps might fail.

## 2. Processing fuzznuc output

This is done by the `process_results.py` script. This cript goes thorugh the fiels produced by
the previous step and after processing the output, it dump sit in JSON files. One JSON file per
input file(Unless the input file had been split in parts in which case the results from teh various
parts are joined in one JSON file.)

## 3. Extracting the sequences

This is done by `extract_sequences.py`. It simply goes through the FASTA files and the JSON 
dictionaries made in the previous step and extracts the relative sequences.

## 4. Create the blast input file

This is done by the `create_fasta_from_json.py` script.  It simply goes through all the JSON files
and dumps them in the `extracted_sequences.fa` file. The ids for each sequence are based on the
fasta file they come from, the strand and the type of LTR(5 or 3 prime). __Due to the unexpectedly
large number of hits in th latter stages of the analysis I introduced an additional check at this point:
Only the hits which have 50bp flanking them are dumped in the out-file.__ The relevant part of the
script in case you would like to modify this behaviour is:

```python
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
```

## 5. Running BLAST

This is controlled by the script `run_blast.py`. One of the default options of this script is that if there
are more than one processors on the system where the analysis is run it will utilise them to speed up
the analysis. However, it will not utilise more than 4 at any given time. (Easily modifiable).

## 6. Optional step - Create the repeating regions Dictionary

Script `extract_repeating_regions.py` takes care of this step. However, this is onl;y required the first time 
the pipeline is run. For all subsequent analyses, you can simply save its output and commetn out the relevant
parts in `pipeline.py`.

## 7. Processing BLAST output

The final step in the analysis. It is done by the `process_blast_output.py` script. Hits which are determined to 
be in a repetitive region are filtered out of the analysis. In addition due to the large number of results I also
limited the analysis to the hits which had a full match in the flanking regions. This is done by this function:

```python
def filter_by_query_length(prime, strand, start, end):
    if (strand == 'forward' and prime == '5_prime') or (strand == 'reverse' and prime == '3_prime'):
        if start == 1 and end == 50:
            return True
        else:
            return False
    elif (strand == 'reverse' and prime == '5_prime') or (strand == 'forward' and prime == '3_prime'):
        if start == 21 and end == 70:
            return True
        else:
            return False
    else:
        raise RuntimeError('Unexpected combination of strand and prime.')
```
