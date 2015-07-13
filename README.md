# herv-py
A python pipeline for the detection of HERV-K elements in modern and ancient Hominid genomes.


# TODO
## Organise the results in a better way:

+ Top level folder -- Results
    - fuzznuc files folder. These are the files produced by _fuzznuc_ through _run_fuzznuc.py_.
    - hits files folder. These are produced by process_results.py_.
    - fasta files folder. These are the input files as wel as the final results, ie the extracted
      sequences. Produced by _extract_sequences.py_.

## Modify the pipeline

1. More helpful print statement. Possibly a % as file size ratio / total.
2. add the subprocess.CalledProcessError to the except maybe
3. separate the three stages(run fuzznuc, check results, extract) in three
   functions

## Write a couple of classes to generalise some things:

- A class to read a directory and return all the contents.
  - Filter the results in the class as an additional argument.
  - Do no t filter anything and do the filtering in the calling part of the code.

- A class for the read processing? Though classes cannot be dumped in JSON objects.
