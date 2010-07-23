#!/usr/bin/env python

import os
import sys

from kugelblitz.translator import translate_string

def compile_file(filename):
    # Work out the destination file
    dest_filename = os.path.splitext(filename)[0] + ".js"
    with open(dest_filename, "w") as dest:
        with open(filename, "r") as src:
            dest.write(translate_string(src.read()))

def main():
    # Read in the filenames from the commandline
    filenames = sys.argv[1:]
    for filename in filenames:
        compile_file(filename)
        print "Compiled %r." % filename

if __name__ == "__main__":
    main()