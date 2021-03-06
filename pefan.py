#! /usr/bin/env python

import sys
import argparse
from random import random
from datetime import datetime
import re
from time import monotonic as monotonic_time

import logging
from logging import debug, info, exception
long_format = "%(asctime)s %(name)16s:%(lineno)-4d (%(funcName)-21s) %(levelname)-8s %(message)s"


# support py2
try:
    BrokenPipeError
except NameError:
    BrokenPipeError = OSError


def parse_opts():
    parser = argparse.ArgumentParser(description='''Tries to emulate Perl's (Yikes!) -peFan switches and more.''',
                                     epilog='''FORMAT can use Python's strftime()'s codes
                                               (see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior).

                                               Automatic switches must be passed after all the other options
                                               recognized by pefan.''')

    parser.add_argument('-A', '--append-logfile', default=None,
                        help='''Also log lines to a file, appending to the end.''')
    parser.add_argument('-a', '--split', action='store_true',
                        help='''Turns on autosplit, so the line is split in elements. The list of
                                elements go in the 'data' variable.''')
    parser.add_argument(      '--debug', action='store_true',
                        help='''Enable debugging info in the stderr.''')
    parser.add_argument('-e', '--script', default=None,
                        help='''The script to run inside the loop.''')
    parser.add_argument('-F', '--split-char', default=None,
                        help='''The field delimiter. This implies [-a|--split].''')
    parser.add_argument('-i', '--ignore-empty', action='store_true',
                        help='''Do not print empty lines.''')
    parser.add_argument('-l', '--logfile', default=None,
                        help='''Also log lines to a file.''')
    parser.add_argument('-M', '--import', dest='module_specs', metavar='MODULE_SPEC',
                        action='append', default = [],
                        help='''Import modules before running any code. MODULE_SPEC can be
                                MODULE or MODULE,NAME,... The latter uses the 'from MODULE import NAME, ...'
                                variant. MODULE or NAMEs can have a :AS_NAME suffix.''')
    parser.add_argument('-m', dest='module_specs', metavar='MODULE_SPEC',
                        action='append', default=[], help='''Same as [-M|--import]''')
    parser.add_argument('-N', '--enumerate-lines', action='store_true', default=False,
                        help='''Prepend each line with its line number, like less -N does.''')
    parser.add_argument('-n', '--iterate', action='store_true', default=True,
                        help='''Iterate over all the lines of inputs. Each line is assigned in the
                                'line' variable. This is the default.''')
    parser.add_argument('-P', '--prefix', default=None,
                        help='''Prefix each line with this text.''')
    parser.add_argument('-p', '--print', action='store_true', dest='print_lines', default=True,
                        help='''Print the resulting line. This is the default.''')
    parser.add_argument(      '--no-print', action='store_false', dest='print_lines',
                        help='''Don't automatically print the resulting line, the script knows what
                                to do with it''')
    parser.add_argument('-r', '--relative', action='store_true', default=False,
                        help='''Print a relative timestamp. This records the time difference between consecutive lines.''')
    parser.add_argument(      '--random', type=float, default=1,
                        help='''Print only a fraction of the output lines.''')
    parser.add_argument('-R', '--remove-ansi', action='store_true',
                        help='''Remove ANSI escape sequences from the text.''')
    parser.add_argument('-S', '--automatic-switches', action='store_true',
                        help='''Parse --foo switches into variables. This creates a variable called 'foo'
                                with value True; --foo[=| ]bar stores 'bar' in 'foo'. This is a way to
                                pass arguments to the scripts.''')
    parser.add_argument('-s', '--setup', default=None, metavar='SETUP_SCRIPT',
                        help='''Code to be run as setup. Run only once after importing modules and
                                before iterating over input.''')
    parser.add_argument(      '--begin', default=None, dest='setup', metavar='SETUP_SCRIPT',
                        help='''Same as -s|--setup.''')
    parser.add_argument(      '--test', action='store_true', help='''Run internal test suite.''')
    parser.add_argument('-t', '--timestamp', nargs='?', metavar='FORMAT', default=None,
                        const='%Y-%m-%dT%H:%M:%S.%f%z',
                        help='''Prepend a timestamp using FORMAT. By default prints it in ISO-8601.''')
    parser.add_argument('-T', '--tear-down', default=None, metavar='TEAR_DOWN_SCRIPT',
                        help='''Code that runs after all input lines are processed.''')
    parser.add_argument(      '--end', default=None, dest='tear_down', metavar='TEAR_DOWN_SCRIPT',
                        help='''Same as -T|--tear-down.''')
    # parser.add_argument('-0', '--null', action='store_true',
    #                     help='''Input items are terminated by a null character instead of by newlines.''')

    # parser.add_argument('files', nargs=argparse.REMAINDER, metavar='FILE',
    #                     help='''Files to process. If ommited or file name is '-', stdin is used. Notice
    #                             you can use '-' at any point in the list; f.i. "foo bar - baz".''')

    opts, more = parser.parse_known_args()
    switches = {}

    if opts.debug:
        logging.basicConfig(level=logging.DEBUG, format=long_format)

    debug((opts, more))

    if opts.automatic_switches:
        switches, more = automatic_switches(more)
    debug((switches, more))

    opts.files = more

    debug((opts, switches))

    # post proc
    # if no files, use stdin
    if len(opts.files) == 0:
        opts.files = [ '-' ]

    if opts.split_char is not None:
        opts.split = True

    # opts.script = braced2python(opts.script)

    if opts.setup is not None:
        opts.setup = braced2python(opts.setup)

    return opts, switches


def automatic_switches(args):
    index = 0
    switches = {}
    extra = []
    name = None

    while index < len(args):
        arg = args[index]

        if arg.startswith('--'):
            name = arg[2:]
            if '=' in name:
                name, value = name.split('=', 1)
                switches[name] = value
                name = None
            else:
                switches[name] = True
        else:
            if name is not None:
                switches[name] = arg
                name = None
            else:
                extra.append(arg)

        index += 1

    return switches, extra


def chomp(s):
    '''Remove trailing \n and \r from s.'''
    index = len(s)
    while index > 0 and s[index - 1] in ('\n', '\r'):
        index -= 1

    return s[:index]


def import_names(opts, globs):
    for module_spec in opts.module_specs:
        debug(module_spec)
        try:
            module_name, names_spec = module_spec.split(',', 1)
        except ValueError:
            module_name = module_spec
            names_spec = ''

        if names_spec == '':
            # simple import
            try:
                module_name, as_name = module_name.split(':')
                # py2's __import__() does not provide a way to specify as_name
                module = __import__(module_name)
                globs[as_name] = module
                debug(globs)
            except ValueError:
                module = __import__(module_name)
                globs[module_name] = module
                debug(globs)
        else:
            # no as_name for module_name
            names =  names_spec.split(',')
            for name_spec in names:
                try:
                    name, as_name = name_spec.split(':')
                    module = __import__(module_name, globs, locals(), [name])
                    globs[as_name] = o
                    debug(globs)
                except ValueError:
                    module = __import__(module_name, globs, locals(), [name_spec])

                    debug(module)
                    globs[name_spec] = getattr(module,  name_spec)
                    debug(globs)


if __name__ == '__main__':
    opts, switches = parse_opts()

    if opts.test:
        test()

    globs = dict(globals())
    locs = switches
    import_names(opts, globs)

    if opts.setup is not None:
        exec(opts.setup, globs, locs)

    logfile = None
    if opts.logfile is not None:
        logfile = open(opts.logfile, 'w+')

    # if also -append-logfile, then append
    if opts.append_logfile is not None:
        logfile = open(opts.append_logfile, 'a+')

    lineno = 1

    if opts.remove_ansi:
        # see https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
        # The above regular expression covers all 7-bit ANSI C1 escape sequences, but not
        # the 8-bit C1 escape sequence openers. The latter are never used in today's UTF-8
        # world where the same range of bytes have a different meaning.
        remover = re.compile(r'''\x1B[@-_][0-?]*[ -/]*[@-~]''')


    for file in opts.files:
        if file == '-':
            file = sys.stdin
        else:
            if not hasattr(file, 'read'):
                try:
                    file = open(file)
                except IOError as e:
                    sys.stderr.write("Could not open file '%s': %s\n" % (file, e.args[1]))
                    continue

        locs['file'] = file

        if opts.relative:
            start = monotonic_time()

        while True:
            try:
                line = file.readline()
            except (BrokenPipeError, KeyboardInterrupt):
                # we're reading from stdin, and the proc at the other end of the pipe died
                # bail out
                break

            # py2 support
            if line == '':
                break

            line = chomp(line)

            if opts.remove_ansi:
                line = remover.sub('', line)

            locs['line'] = line

            if opts.split:
                locs['data'] = line.split(opts.split_char)

            if opts.script is not None:
                debug(repr(opts.script))
                exec(opts.script, globs, locs)
                line = locs['line']

            if ( opts.print_lines and (not opts.ignore_empty or line != '') and
                 (opts.random == 1 or random() < opts.random) ):

                if opts.prefix:
                    line = opts.prefix + " " + line

                if opts.relative:
                    end = monotonic_time()
                    line = "(%10.3f): %s" % (end-start, line)
                    start = end

                if opts.timestamp is not None:
                    time = datetime.now()
                    ts = time.strftime(opts.timestamp)
                    line = ts + ': ' + line

                if opts.enumerate_lines:
                    # '       1 '
                    line = ("%8d " % lineno) + line
                    lineno += 1

                print(line)

                if logfile is not None:
                    logfile.write(line+'\n')

    if opts.tear_down is not None:
        exec(opts.tear_down, globs, locs)
