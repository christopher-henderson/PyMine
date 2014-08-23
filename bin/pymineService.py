from bin.decorators import ParseArgs
from bin.classes.daemonHandler import DaemonHandler
import readline
import os

HOME = os.path.dirname(os.path.realpath(__file__))

@ParseArgs
def main(interactive, args):
    pymine = DaemonHandler(HOME)
    if interactive:
        readline.parse_and_bind('set editing-mode vi')
        print ('PyMine version 1.0')
        print ('Type "pmhelp", "copyright" or "license" for more information.')
        command = raw_input('>>> ').strip()
        while command != 'exit':
            pymine.runCommand(command)
            command = raw_input('>>> ').strip()
    else:
        pymine.runCommand(args)