#!/usr/bin/env python

from distutils.core import setup
import py2exe

setup(
    options = {
        'py2exe': {
            'dll_excludes'  : ['msvcr71.dll', 'w9xpopen.exe'],
            'compressed'    : 1,
            'optimize'      : 2,
            'ascii'         : 1,
            'bundle_files'  : 1,
            'packages'      : ['encodings', 'os', 'xml']}
        },
    zipfile = None,
    console = ["cycle_submit.py"]
)
