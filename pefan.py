#! /usr/bin/env python

import sys
import argparse


def parse_opts():
    parser = argparse.ArgumentParser(description='''Tries to emulate Perl's (Yikes!) -epFan switches.''')

    parser.add_argument('-a', '--split', action='store_true',
                        help='''Turns on autosplit, so the line is split in elements. The list of e
                                lements go in the 'data' variable.''')
    parser.add_argument('-e', '--script', required=True,
                        help='''The scipt to run inside the loop.''')
    parser.add_argument('-F', '--split-char', default=None,
                        help='''The field delimiter. This implies [-a|--split].''')
    parser.add_argument('-i', '--ignore-empty', action='store_true',
                        help='''Do not print empty lines.''')
    parser.add_argument('-M', '--import', dest='module_specs', metavar='MODULE_SPEC',
                        action='append', default = [],
                        help='''Import modules before runing any code. MODULE_SPEC can be
                                MODULE or MODULE,NAME,... The latter uses the 'from MODULE import NAME, ...'
                                variant. MODULE or NAMEs can have a :AS_NAME suffix.''')
    parser.add_argument('-m', dest='module_specs', metavar='MODULE_SPEC',
                        action='append', default = [], help='''Same as [-M|--import]''')
    parser.add_argument('-n', '--iterate', action='store_true', default=True,
                        help='''Iterate over all the lines of inputs. Each line is assigned in the
                                'line' variable. This is the default.''')
    parser.add_argument('-p', '--print', action='store_true', dest='print_lines', default=True,
                        help='''Print the resulting line. This is the default.''')
    parser.add_argument(      '--no-print', action='store_false', dest='print_lines',
                        help='''Don't automatically print the resulting line, the script knows what
                                to do with it''')
    parser.add_argument('-s', '--setup', default=None,
                        help='''Code to be run as setup. Run only once after importing modules and
                                before iterating over input.''')
    parser.add_argument('files', nargs=argparse.REMAINDER, metavar='FILE',
                        help='''Files to process. If ommited or file name is '-', stdin is used. Notice
                                you can use '-' at any point in the list; f.i. "foo bar - baz".''')

    opts = parser.parse_args(sys.argv[1:])
    # print(opts)

    # post proc
    # if no files, use stdin
    if len(opts.files) == 0:
        opts.files = [ '-' ]

    if opts.split_char is not None:
        opts.split = True

    return opts


def chomp(s):
    '''Remove trailing \n from s.'''
    index = len(s)
    while index > 0 and s[index - 1] == "\n":
        index -= 1

    return s[:index]


def import_names(opts, globs):
    for module_spec in opts.module_specs:
        # print(module_spec)
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
                # print(globs)
            except ValueError:
                module = __import__(module_name)
                globs[module_name] = module
                # print(globs)
        else:
            # no as_name for module_name
            names =  names_spec.split(',')
            for name_spec in names:
                try:
                    name, as_name = name_spec.split(':')
                    module = __import__(module_name, globs, locals(), [name])
                    globs[as_name] = o
                    # print(globs)
                except ValueError:
                    module = __import__(module_name, globs, locals(), [name_spec])

                    # print(module)
                    globs[name_spec] = getattr(module,  name_spec)
                    # print(globs)


if __name__ == '__main__':
    opts = parse_opts()
    # print(opts)

    globs = dict(globals())
    locs = {}
    import_names(opts, globs)

    if opts.setup is not None:
        opts.setup = braced2python(opts.setup)

        exec(opts.setup, globs, locs)

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

        for line in file:
            locs['line'] = line

            if opts.split:
                locs['data'] = line.split(opts.split_char)

            exec(opts.script, globs, locs)
            line = chomp(locs['line'])


            if opts.print_lines and (not opts.ignore_empty or line != ''):
                print(line)
