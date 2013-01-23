#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

__docstring__ =\
"""Utilities to build CNF formulas interesting for proof complexity.

The module `dimacs` contains facilities to generate manipulates dimacs
CNFs, in particular from command line.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import copy
import sys
import random
from cnfgen import CNF

def read_dimacs_file(file_handle):
    """Load dimacs file into a CNF object
    """
    cnf=CNF()

    n = -1  # negative signal that spec line has not been read
    m = -1

    line_counter=0
    clause_counter=0
    literal_buffer=[]

    for l in file_handle.readlines():

        line_counter+=1

        # add the comment to the header or in the middle
        if l[0]=='c':
            if n<0:
                cnf.header = cnf.header+l[2:]
            else:
                cnf.add_comment(l[2:])
            continue

        # parse spec line
        if l[0]=='p':
            if n>=0:
                raise ValueError("Syntax error: "+
                                 "line {} contains a second spec line.".format(line_counter))
            _,_,nstr,mstr = l.split()
            n = int(nstr)
            m = int(mstr)
            for i in range(1,n+1):
                cnf.add_variable(str(i))
            continue

        # parse literals
        for lv in [int(lit) for lit in l.split()]:
            if lv==0:
                cnf._add_compressed_clauses([tuple(literal_buffer)])
                literal_buffer=[]
                clause_counter +=1
            else:
                literal_buffer.append(lv)

    # Checks at the end of parsing
    if len(literal_buffer)>0:
        raise ValueError("Syntax error: last clause was incomplete")

    if m=='-1':
        raise ValueError("Warning: empty input formula ")

    if m!=clause_counter:
        raise ValueError("Warning: input formula "+
                         "contains {} instead of expected {}.".format(clause_counter,m))

    # return the formula
    cnf._check_coherence(force=True)
    return cnf


def command_line_reshuffle(argv):

    # Python 2.6 does not have argparse library
    try:
        import argparse
    except ImportError:
        print("Sorry: %s requires `argparse` library, which is missing.\n"%argv[0],file=sys.stderr)
        print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
        print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
        print(" * http://code.google.com/p/argparse",file=sys.stderr)
        print("",file=sys.stderr)
        exit(-1)

    # Parse the command line arguments
    parser=argparse.ArgumentParser(prog='shuffle',epilog="""
    For more information type 'shuffle <formula type> [--help | -h ]'
    """)

    parser.add_argument('--output','-o',
                        type=argparse.FileType('wb',0),
                        metavar="<output>",
                        default='-',
                        help="""Output file. The formula is saved
                        on file instead of being sent to standard
                        output. Setting '<output>' to '-' is another
                        way to send the formula to standard output.
                        (default: -)
                        """)
    parser.add_argument('--seed','-S',
                        metavar="<seed>",
                        default=None,
                        type=str,
                        action='store',
                        help="""Seed for any random process in the
                        program. Any python hashable object will
                        be fine.  (default: current time)
                        """)
    parser.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. A formula in dimacs format. Setting '<input>' to '-' is
                        another way to read from standard input.
                        (default: -)
                        """)

    g=parser.add_mutually_exclusive_group()
    g.add_argument('--verbose', '-v',action='count',default=1,
                   help="""Include comments inside the formula. It may
                   not be supported by very old sat solvers.
                   """)
    g.add_argument('--quiet', '-q',action='store_const',const=0,dest='verbose',
                   help="""Output just the formula with not header
                   or comment.""")


    # Process the options
    args=parser.parse_args()

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    input_cnf=read_dimacs_file(args.input)

    output_cnf=CNF(input_cnf.get_clauses_and_comments(),input_cnf.header)

    # Do we wnat comments or not
    output_comments=args.verbose >= 2
    output_header  =args.verbose >= 1

    output = output_cnf.dimacs(add_header=output_header,
                           add_comments=output_comments)
    print(output,file=args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_reshuffle(sys.argv)