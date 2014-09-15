from __future__ import print_function
from datetime import date

PyMineCopyright = '''
Copyright (c) {YEAR} Christopher Henderson.
Minecraft is a trademark of Notch Development AB.
Visit https://account.mojang.com/documents/minecraft_eula for more information regarding the Minecraft EULA.
'''.format(YEAR=date.today().year)

def printCopyright():
    print (PyMineCopyright)
