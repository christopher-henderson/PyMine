from src.debug import Logger
from .parseArgs import ParseArgs
from .daemonHandler import DaemonHandler
from readline import parse_and_bind

@ParseArgs
def main(interactive, args):
    pymine = DaemonHandler()
    if interactive:
        parse_and_bind('set editing-mode vi')
        print ('PyMine version v1.1')
        print ('Type "pmhelp", "copyright" or "license" for more information.')
        command = raw_input('>>> ').strip()
        while command != 'exit':
            pymine.runCommand(command)
            command = raw_input('>>> ').strip()
    else:
        pymine.runCommand(args)