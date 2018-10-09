This tool is intended to be used for the inclusion os Python snippets in shell
scripts. It accepts the same options as `perl`, namely, `-p`, `-e`, `-F`, `-a`
and `-n` (hence its name :), plus several others, and --long-option versions too,
which I consider better for self documenting scripts.

```
usage: pefan.py [-h] [-a] [--debug] -e SCRIPT [-F SPLIT_CHAR] [-i]
                [-M MODULE_SPEC] [-m MODULE_SPEC] [-N] [-n] [-p] [--no-print]
                [-r RANDOM] [-s SETUP] [--test] [-t [FORMAT]]
                ...

Tries to emulate Perl's (Yikes!) -epFan switches.

positional arguments:
  FILE                  Files to process. If ommited or file name is '-',
                        stdin is used. Notice you can use '-' at any point in
                        the list; f.i. "foo bar - baz".

optional arguments:
  -h, --help            show this help message and exit
  -a, --split           Turns on autosplit, so the line is split in elements.
                        The list of e lements go in the 'data' variable.
  --debug               Enable debugging info in the stderr.
  -e SCRIPT, --script SCRIPT
                        The script to run inside the loop.
  -F SPLIT_CHAR, --split-char SPLIT_CHAR
                        The field delimiter. This implies [-a|--split].
  -i, --ignore-empty    Do not print empty lines.
  -M MODULE_SPEC, --import MODULE_SPEC
                        Import modules before runing any code. MODULE_SPEC can
                        be MODULE or MODULE,NAME,... The latter uses the 'from
                        MODULE import NAME, ...' variant. MODULE or NAMEs can
                        have a :AS_NAME suffix.
  -m MODULE_SPEC        Same as [-M|--import]
  -N, --enumerate-lines
                        Prepend each line with its line number, like less -N
                        does.
  -n, --iterate         Iterate over all the lines of inputs. Each line is
                        assigned in the 'line' variable. This is the default.
  -p, --print           Print the resulting line. This is the default.
  --no-print            Don't automatically print the resulting line, the
                        script knows what to do with it
  -r RANDOM, --random RANDOM
                        Print only a fraction of the output lines.
  -s SETUP, --setup SETUP
                        Code to be run as setup. Run only once after importing
                        modules and before iterating over input.
  --test                Run internal test suite.
  -t [FORMAT], --timestamp [FORMAT]
                        Prepend a timestamp using FORMAT. By default prints it
                        in ISO-8601.
```

Unlike `perl`, `-n` and `-p` are implicit. To disable the latter one, use
`--no-print`.

The script is run inside a loop that reads each line of all the input files and
stores it in the variable `line`. Your script can the use it to do its stuff.
That variable will be printed at the end of the loop.

If `--split` is used, the line's elements are stored in a list called `data`.

I added three options that I have implemented gazillion of times in several ways.
Those are `--ramdom`, `--enumerate` and `--timestamp`. The latter accepts
Python's `strftime()`'s codes (see
[the docs](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)).

`--test` and `--debug` should never been used outside development situations.
