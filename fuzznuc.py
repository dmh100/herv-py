__author__ = 'Panagiotis Koukos'

"""
fuzznuc.py - Scan input files with fuzznuc.

This module scans the input files for the presence of the specified
nucleotide sequence and stores the results in an aptly named text file.

:param -i, --in: Path to the file which contains the sequences to parse.
:type -i, --in: str or unicode
:param -p, --pat: Path to the file which contains the pattern to use.
:type -p, --pat: str or unicode
:param -o, --out: What file to write the results in.
:type -o, --out: str or unicode
:return None
"""

# import argparse
import subprocess
# import sys

# From http://stackoverflow.com/a/11270665
try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


def check_fuzznuc():
    """
    Check for the presence of fuzznuc in the local system.

    This functions uses the linux built in command 'which' to
    check if the command fuzznuc is available.

    :param : none
    :return: The absolute path to the fuzznuc program as returned
             by which on success, None on failure.
    """

    try:
        # stdout=DEVNULL suppresses the output of the system call.
        subprocess.check_call(['which', 'fuzznuc'], stdout=DEVNULL)
    except subprocess.CalledProcessError:
        print 'Unable to locate fuzznuc on the local system. Aborting.'
        return None
    finally:
        DEVNULL.close()

    fuzznuc = subprocess.check_output(['which', 'fuzznuc']).rstrip()
    return fuzznuc

# print check_fuzznuc()
