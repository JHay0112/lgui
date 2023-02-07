#!/usr/bin/env python3
"""glcapy V0.0.1
Copyright (c) 2023 Michael P. Hayes, UC ECE, NZ

Usage: glcapy [infile.sch]
"""

from argparse import ArgumentParser
import sys
from lcapygui.ui.tk.lcapytkm import LcapyTkM
from lcapygui.ui.tk.lcapytk import LcapyTk


def schtex_exception(type, value, tb):
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        # We are not in interactive mode or we don't have a tty-like
        # device, so call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback
        import pdb
        # We are in interactive mode, print the exception...
        traceback.print_exception(type, value, tb)
        print()
        # ...then start the debugger in post-mortem mode.
        pdb.pm()


def main(argv=None):

    if argv is None:
        argv = sys.argv

    parser = ArgumentParser(
        description='Generate lcapy netlists.')
    parser.add_argument('--version', action='version',
                        version=__doc__.split('\n')[0])
    parser.add_argument('--pdb', action='store_true',
                        default=False,
                        help="enter python debugger on exception")
    parser.add_argument('--debug', type=int,
                        dest='debug', default=None,
                        help="enable debugging")
    parser.add_argument('filename', type=str, nargs='?',
                        help='schematic filename', default=None)
    parser.add_argument('--ui', type=str, default='tk',
                        help="choose UI")

    args = parser.parse_args()

    if args.pdb:
        sys.excepthook = schtex_exception

    if args.ui == 'tkm':
        e = LcapyTkM(args.filename, debug=args.debug)
    else:
        e = LcapyTk(args.filename, debug=args.debug)

    e.display()

    return 0


if __name__ == '__main__':
    sys.exit(main())
