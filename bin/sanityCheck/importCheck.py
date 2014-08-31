from __future__ import print_function
import sys
imports = {'daemon': 'python-daemon',
           'psutil': 'psutil',
           'yaml': 'pyyaml'
           }

def checkImport(module):
    try:
        __import__(module)
    except ImportError as e:
        print (e)
        print ('You are appear to be missing the {MODULE} module.'.format(MODULE=module))
        print ('Try "sudo pip install {MOD_NAME}"'.format(MOD_NAME=imports[module]))
        return False
    else:
        return True

def checkImports():
    errors = []
    for module in imports:
        errors.append(checkImport(module))
    if any(errors):
        sys.exit(1)