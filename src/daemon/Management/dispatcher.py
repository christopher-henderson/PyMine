from .parser import Parser
from .demultiplexer import Demultiplexer
from src.PyMineExceptions import PyMineException

class Dispatcher(object):

    #===========================================================================
    # @TODO use, add and remove don't have a return to print out,
    # causing a type error in this current setup.
    #===========================================================================

    def __init__(self):
        self.demux = Demultiplexer()
        self.commandMap = {'start': self.demux.startServer,
                           'stop': self.demux.stopServer,
                           'restart': self.demux.restartServer,
                           #'status': self.demux.getStatus,
                           #'backup': self.demux.backupServer,
                           'use': self.demux.useServer,
                           'add': self.demux.addServer,
                           'remove': self.demux.removeServer
                           }

    def __enter__(self):
        for response in self.demux.startServer(pattern='.*'):
            #===================================================================
            # It is necessary to iterate over the returned
            # generator, otherwise self is returned immediately
            # despite the startup process being incomplete.
            #===================================================================
            pass
        return self

    def __exit__(self, type, value, traceback):
        self.demux.stopServer(pattern='.*')

    def execute(self, userInput):
        command,pattern = Parser.parse(userInput)
        try:
            if command in self.commandMap:
                return self.commandMap[command](pattern=pattern)
            else:
                return self.demux.forwardCommand(command, pattern=pattern)
        except PyMineException as e:
            return [e]
