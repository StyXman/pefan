#! /usr/bin/env python

import sys
import argparse
import random

import logging
from logging import debug, info, exception
long_format = "%(asctime)s %(name)16s:%(lineno)-4d (%(funcName)-21s) %(levelname)-8s %(message)s"


# states for the state machine
class NormalCode:
    ''''''

class SemiColon:
    ''';'''

class LineSplit:
    ''' '''

class Block1:
    ''' '''

class BlockStart2:
    '''{'''

class BlockStart3:
    ''' '''

class BlockEnd2:
    '''}'''

class BlockEnd3:
    ''' '''

class Quoted1:
    """'"""

class Quoted2:
    """'"""

class Quoted3:
    """'"""


delta = {
    (NormalCode,  ';'): SemiColon,
    (SemiColon,   ' '): LineSplit,

    (NormalCode,  ' '): Block1,
    (Block1,      ' '): Block1,

    (Block1,      '{'): BlockStart2,
    (BlockStart2, ' '): BlockStart3,
    (BlockStart3, ' '): BlockStart3,

    (Block1,      '}'): BlockEnd2,
    (BlockEnd2,   ' '): BlockEnd3,
    (BlockEnd3,   ' '): BlockEnd3,

    (NormalCode,  "'"): Quoted1,
    (Quoted1,     "'"): Quoted2,
    (Quoted3,     "'"): Quoted3,
}


def make_line(indent, part):
    return ('    ' * indent) + (''.join(part))


def braced2python(s):
    indent = 0
    # we'll do the join() trick, twice
    parts = []
    part = []
    state = NormalCode

    # the easiest way I can see to do this is to do a char scan
    # whith a whole state machine full of hacks and special cases
    for index, c in enumerate(s):
        new_state = delta.get((state, c), None)
        debug([state.__name__, c, new_state])
        part.append(c)
        debug(part)

        if new_state is not None:
            state = new_state

            if state == LineSplit:
                # backtrack, remove '; '
                part = part[:-2]
                parts.append(make_line(indent, part))
                part = []

                state = NormalCode

            elif state == BlockStart3:
                # backtrack, remove ' { '
                part = part[:-3]
                debug(part)
                # and add the trailing colon
                part.append(':')
                debug(part)

                parts.append(make_line(indent, part))
                part = []
                indent += 1

                # this is a shortcut
                state = NormalCode
            elif state == BlockEnd3:
                part = part[:-3]
                debug(part)

                parts.append(make_line(indent, part))
                part = []
                indent -= 1

                state = Block1
        else:
            state = NormalCode

        debug([part, parts])

    # handle last ' }'
    if state == BlockEnd2:
        part = part[:-2]
        debug(part)

    if len(part) != 0:
        parts.append(make_line(indent, part))
    else:
        # HACK to add the trailing \n
        parts.append('')

    return '\n'.join(parts)


def ass(a, b):
    if not a == b:
        print(a)
        print(b)
        raise AssertionError((a, b))


def test():
    ass(braced2python('''if True { a = 3 } '''), '''if True:
    a = 3
''')

    ass(braced2python('''if True { a = 3; if False { b = 4 } else { c = 5 } }'''), '''if True:
    a = 3
    if False:
        b = 4
    else:
        c = 5
''')
    return

    ass(braced2python('''if True { '''), '''if True:
''')

    c = '''if True { ok = ' {  } ' } else { if False { ok_nok = " {  } "; exit() } else { ok_ok = """ { a } """ } }'''
    assert braced2python(c) == '''if True:
    ok = True
else:
    if False:
        ok_nok = True
        exit()
    else
        ok_ok = True
'''

    c = '''line = " ".join(data[5:-10]); if random.random() < 0.01 { print(line) }'''
    assert braced2python(c) == '''line = " ".join(data[5:-10])
if random.random() < 0.01:
    print(line)
'''

    print('A-OK')
    sys.exit(0)


# finished with that mess
def parse_opts():
    parser = argparse.ArgumentParser(description='''Tries to emulate Perl's (Yikes!) -epFan switches.''')

    parser.add_argument('-a', '--split', action='store_true',
                        help='''Turns on autosplit, so the line is split in elements. The list of e
                                lements go in the 'data' variable.''')
    parser.add_argument(      '--debug', action='store_true',
                        help='''Enable debugging info in the stderr.''')
    parser.add_argument('-e', '--script', required=True,
                        help='''The script to run inside the loop.''')
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
    parser.add_argument('-N', '--enumerate-lines', action='store_true', default=False,
                        help='''Prepend each line with its line number, like less -N does.''')  # '       1 '
    parser.add_argument('-n', '--iterate', action='store_true', default=True,
                        help='''Iterate over all the lines of inputs. Each line is assigned in the
                                'line' variable. This is the default.''')
    parser.add_argument('-p', '--print', action='store_true', dest='print_lines', default=True,
                        help='''Print the resulting line. This is the default.''')
    parser.add_argument(      '--no-print', action='store_false', dest='print_lines',
                        help='''Don't automatically print the resulting line, the script knows what
                                to do with it''')
    parser.add_argument('-r', '--random', type=float, default=1,
                        help='''Print only a fraction of the output lines.''')
    parser.add_argument('-s', '--setup', default=None,
                        help='''Code to be run as setup. Run only once after importing modules and
                                before iterating over input.''')
    parser.add_argument(      '--test', action='store_true', help='''Run internal test suite.''')

    parser.add_argument('files', nargs=argparse.REMAINDER, metavar='FILE',
                        help='''Files to process. If ommited or file name is '-', stdin is used. Notice
                                you can use '-' at any point in the list; f.i. "foo bar - baz".''')

    opts = parser.parse_args(sys.argv[1:])
    if opts.debug:
        logging.basicConfig(level=logging.DEBUG, format=long_format)
    debug(opts)

    # post proc
    # if no files, use stdin
    if len(opts.files) == 0:
        opts.files = [ '-' ]

    if opts.split_char is not None:
        opts.split = True

    opts.script = braced2python(opts.script)

    if opts.setup is not None:
        opts.setup = braced2python(opts.setup)

    return opts


def chomp(s):
    '''Remove trailing \n from s.'''
    index = len(s)
    while index > 0 and s[index - 1] == "\n":
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
    opts = parse_opts()
    debug(opts)

    if opts.test:
        test()

    globs = dict(globals())
    locs = {}
    import_names(opts, globs)

    if opts.setup is not None:
        exec(opts.setup, globs, locs)

    lineno = 1

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
            locs['line'] = chomp(line)

            if opts.split:
                locs['data'] = line.split(opts.split_char)

            debug(repr(opts.script))
            exec(opts.script, globs, locs)
            line = locs['line']

            if ( opts.print_lines and (not opts.ignore_empty or line != '') and
                 (opts.random == 1 or random.random() < opts.random) ):

                if opts.enumerate_lines:
                    # '       1 '
                    line = ("%8d " % lineno) + line
                    lineno += 1

                print(line)
