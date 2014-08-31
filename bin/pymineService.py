from bin.sanityCheck.importCheck import checkImports
checkImports()
from bin.decorators import ParseArgs
from bin.classes.daemonHandler import DaemonHandler
import readline

@ParseArgs
def main(interactive, args):
    pymine = DaemonHandler()
    if interactive:
        readline.parse_and_bind('set editing-mode vi')
        print ('PyMine version v1.1')
        print ('Type "pmhelp", "copyright" or "license" for more information.')
        command = raw_input('>>> ').strip()
        while command != 'exit':
            pymine.runCommand(command)
            command = raw_input('>>> ').strip()
    else:
        pymine.runCommand(args)
