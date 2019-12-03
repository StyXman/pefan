This tool is intended to be used for the inclusion os Python snippets in shell
scripts. It accepts the same options as `perl`, namely, `-p`, `-e`, `-F`, `-a`
and `-n` (hence its name :), plus several others, and --long-option versions too,
which I consider better for self documenting scripts.

```
usage: pefan.py [-h] [-A APPEND_LOGFILE] [-a] [--debug] [-e SCRIPT]
                [-F SPLIT_CHAR] [-i] [-l LOGFILE] [-M MODULE_SPEC]
                [-m MODULE_SPEC] [-N] [-n] [-P PREFIX] [-p] [--no-print]
                [-r RANDOM] [-R] [-S] [-s SETUP] [--test] [-t [FORMAT]] [-0]

Tries to emulate Perl's (Yikes!) -peFan switches and more.

optional arguments:
  -h, --help            show this help message and exit
  -A APPEND_LOGFILE, --append-logfile APPEND_LOGFILE
                        Also log lines to a file, appending to the end.
  -a, --split           Turns on autosplit, so the line is split in elements.
                        The list of e lements go in the 'data' variable.
  --debug               Enable debugging info in the stderr.
  -e SCRIPT, --script SCRIPT
                        The script to run inside the loop.
  -F SPLIT_CHAR, --split-char SPLIT_CHAR
                        The field delimiter. This implies [-a|--split].
  -i, --ignore-empty    Do not print empty lines.
  -l LOGFILE, --logfile LOGFILE
                        Also log lines to a file.
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
  -P PREFIX, --prefix PREFIX
                        Prefix each line with this text.
  -p, --print           Print the resulting line. This is the default.
  --no-print            Don't automatically print the resulting line, the
                        script knows what to do with it
  -r RANDOM, --random RANDOM
                        Print only a fraction of the output lines.
  -R, --remove-ansi     Remove ANSI escape sequences from the text.
  -S, --automatic-switches
                        Automaticalle parse --foo switches. This creates a
                        variable called 'foo' with value True; --foo[=| ]bar
                        stores 'bar' in 'foo'.
  -s SETUP, --setup SETUP
                        Code to be run as setup. Run only once after importing
                        modules and before iterating over input.
  --test                Run internal test suite.
  -t [FORMAT], --timestamp [FORMAT]
                        Prepend a timestamp using FORMAT. By default prints it
                        in ISO-8601.
  -0, --null            Input items are terminated by a null character instead
                        of by newlines.

FORMAT can use Python's strftime()'s codes (see
https://docs.python.org/3/library/datetime.html#strftime-and-strptime-
behavior). Automatic switches must be passed after all the other options
recognized by pefan.
```

Unlike `perl`, `-n` and `-p` are implicit. To disable the latter one, use
`--no-print`.

The script is run inside a loop that reads each line of all the input files and
stores it in the variable `line`. Your script can then use it to do its stuff.
That variable will be printed at the end of the loop.

If `--split` is used, the line's elements are stored in a list called `data`, and
you need to assing something to `line`, otherwise it will print the original line.

I added three options that I have implemented gazillion of times in several ways.
Those are `--ramdom`, `--enumerate` and `--timestamp`. The latter accepts
Python's `strftime()`'s codes (see
[the docs](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)).

`--test` and `--debug` should never been used outside development situations.
