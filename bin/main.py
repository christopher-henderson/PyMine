#!/usr/bin/env python
from __future__ import print_function
from bin.decorators import ParseArgs
from bin.daemonHandler import DaemonHandler
import readline
import sys
import os

MINECRAFT = '/opt/minecraft/minecraft.jar'
PIDFILE = '/var/run/pymine/pymine.pid'
UNIX_SOCKET = '/var/run/pymine/pymine.sock'
MIN_MEMORY = '1G'
MAX_MEMORY = '1G'
USER = 'minecraft'
BACKUP_DIR = '/opt/minecraft/backups'
HOME = os.path.dirname(os.path.realpath(__file__))

@ParseArgs(sys.argv[:])
def main(interactive, args):
    pymine = DaemonHandler(HOME, MINECRAFT, PIDFILE, UNIX_SOCKET, MIN_MEMORY, MAX_MEMORY, USER, BACKUP_DIR)
    if interactive:
        readline.parse_and_bind('set editing-mode vi')
        print ('PyMine version 0.1')
        print ('Type "help", "copyright", "credits" or "license" for more information.')
        command = raw_input('>>> ').strip()
        while command != 'exit':
            pymine.runCommand(command)
            command = raw_input('>>> ').strip()
    else:
        pymine.runCommand(args)
  
#===============================================================================
# try:
#     main()
# except KeyboardInterrupt as error:
#     print (error)
#===============================================================================