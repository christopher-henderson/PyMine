from __future__ import print_function

PyMineHelp = '''
Usage: pymine [command]

If no command is given then PyMine enters into an interactive session.

PyMine Options:

start                   Start the Minecraft server
stop                    Stop the Minecraft server
restart                 Restart the Minecraft server
copyright               Print the copyright message
license                 Print the software license
pmhelp                  Print this help message
                            ("help" is passed onto Minecraft)

Any commands that do not match the above are passed onto the Minecraft server for parsing.
If the Minecraft server is not running but an arbitrary Minecraft command was given then
PyMine will simply return an "Invalid Command".
'''

def printHelp():
    print (PyMineHelp)