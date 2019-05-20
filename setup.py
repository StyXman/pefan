#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2019 Marcos Dione <mdione@grulic.org.ar>
# for licensing details see the file LICENSE

from distutils.core import setup

setup (
    name='pefan',
    version= '0.1a',
    description= 'Run Python code over line-based input streams.',
    long_description='''Similarly to awk, sed -e and perl -e, execute Python code
    within a loop that reads from input files and print the result at the end.''',
    author= 'Marcos Dione',
    author_email= 'mdione@grulic.org.ar',
    url= 'https://github.com/StyXman/pefan',
    scripts= [ 'pefan.py' ],
    license= 'GPLv3',
    classifiers= [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
        ],
    )
