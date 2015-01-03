from Daemon.Utilities.parser import Parser
from Common.PyMineExceptions import *

class Communicator(object):

    #===========================================================================
    # @TODO use, add and remove don't have a return to print out,
    # causing a type error in this current setup.
    #===========================================================================

    def __init__(self, multicaster, socket):
        self.multicaster = multicaster
        self.socket = socket
        self.commandMap = {'start': multicaster.startServer,
                           'stop': multicaster.stopServer,
                           'restart': multicaster.restartServer,
                           'use': multicaster.useServer,
                           'add': multicaster.addServer,
                           'remove': multicaster.removeServer
                           }

    def execute(self, userInput):
        command,pattern = Parser.parse(userInput)
        try:
            if command in self.commandMap:
                response = self.commandMap[command](pattern=pattern)
            else:
                response = self.multicaster.forwardCommand(command, pattern=pattern)
        except PyMineException as e:
            self._sendResponse([e])
        else:
            if command == 'restart':
                self._sendNestedResponse(response)
            else:
                self._sendResponse(response)

    def _sendResponse(self, response):
        for line in response:
            self.socket.send(line)
            #print line

    def _sendNestedResponse(self, response):
        for generator in response:
            self._sendResponse(generator)
