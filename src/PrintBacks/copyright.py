from __future__ import print_function
from datetime import date

PyMineCopyright = '''
Copyright (c) {YEAR} Christopher Henderson.
All Rights Reserved.
'''.format(YEAR=date.today().year)

def printCopyright():
    print (PyMineCopyright)