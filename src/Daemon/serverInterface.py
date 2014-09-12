from re import match
from itertools import chain
from src.Daemon.minecraftHandler import Minecraft
import src.Utilities.PyMineExceptions as PyMineExceptions

class ServerInterface(object):
    
    def __init__(self, **kwargs):
        self.servers = {serverName: Minecraft(javaArgs) for serverName,javaArgs in kwargs.items()}
        self.using = None #@TODO Need to figure out a default

    def __iter__(self):
        for name in sorted((server for server in self.servers)):
            yield name

    def __enter__(self):
        self.startServer(regex='*')

    def __exit__(self):
        self.stopServer(regex='*')

    def addServer(self, serverName, javaArgs):
        '''
        Adds the specified Minecraft server to the currently running
        instance of PyMine. The new Minecraft server is not automatically
        started.
        
        Raises PyMineExceptions.DuplicateMinecraftServer if there already
        exists a Minecraft server by that name.
        '''
        if serverName not in self.servers:
            self.servers[serverName] = Minecraft(javaArgs)
        else:
            raise PyMineExceptions.DuplicateMinecraftServer(serverName)

    def removeServer(self, serverName):
        '''
        Cleanly stops and removes the specified Minecraft server from
        the currently running instance of PyMine.
        
        Raises PyMineExceptions.NoSuchMinecraftServer if the name of
        the Minecraft server could not be found.
        '''
        if serverName in self.servers:
            self.servers[serverName].stop()
            del self.servers[serverName]
        else:
            raise PyMineExceptions.NoSuchMinecraftServer(serverName)
    
    def useServer(self, serverName):
        '''
        Changes the interface to handling the specified Minecraft server.
        
        Raises PyMineExceptions.NoSuchMinecraftServer if the name of
        the Minecraft server could not be found.
        '''
        if serverName in self.servers:
            self.using = serverName
        else:
            raise PyMineExceptions.NoSuchMinecraftServer(serverName)

    #===========================================================================
    # @TODO Issue #9.
    # These need decorators/closures/SOMETHING. Too much repetition.
    #
    # How do I capture the regex in the dec/clos?
    # ...could tweak the SelfAwareDecorator
    #===========================================================================

    def startServer(self, regex=None):
        '''
        Default behavior to is to start the currently selected Minecraft
        server.
        
        If a regular expression is given then all servers whose name matches
        the regular expression will be started.

        Returns a generator of the responses.
        '''
        if regex is None:
            self.servers[self.using].start()
        else:
            #===================================================================
            # https://docs.python.org/2/library/itertools.html#itertools.chain
            # 
            # "Make an iterator that returns elements from the first iterable until it is exhausted,
            # then proceeds to the next iterable, until all of the iterables are exhausted."
            # 
            # The use here is to make sure that one coherent iterable is returned in both cases.
            #===================================================================
            return chain(*[self.servers[server].start() for server in self.__iter__() if match(regex, server)])

    def stopServer(self, regex=None):
        '''
        Default behavior to is to stop the currently selected Minecraft
        server.

        If a regular expression is given then all servers whose name matches
        the regular expression will be stopped.

        Returns a generator of the responses.
        '''
        if regex is None:
            return self.servers[self.using].stop()
        else:
            #===================================================================
            # https://docs.python.org/2/library/itertools.html#itertools.chain
            # 
            # "Make an iterator that returns elements from the first iterable until it is exhausted,
            # then proceeds to the next iterable, until all of the iterables are exhausted."
            # 
            # The use here is to make sure that one coherent iterable is returned in both cases.
            #===================================================================
            return chain(*[self.servers[server].stop() for server in self.__iter__() if match(regex, server)])

    def restartServer(self, regex=None):
        '''
        Default behavior to is to stop the currently selected Minecraft
        server.
        
        If a regular expression is given then all servers whose name matches
        the regular expression will be stopped.
        
        Returns a generator of the responses.
        '''
        if regex is None:
            self.servers[self.using].restart()
        else:
            #===================================================================
            # https://docs.python.org/2/library/itertools.html#itertools.chain
            # 
            # "Make an iterator that returns elements from the first iterable until it is exhausted,
            # then proceeds to the next iterable, until all of the iterables are exhausted."
            # 
            # The use here is to make sure that one coherent iterable is returned in both cases.
            #===================================================================
            
            # needs restasrt logic
            return chain(*[self.servers[server].restart() for server in self.__iter__() if match(regex, server)])

    def forwardCommand(self, command, regex=None):
        '''
        Default behavior to is to forward a command to the currently selected Minecraft
        server.
        
        If a regular expression is given then all servers whose name matches
        the regular expression will be passed the command.
        
        Returns a generator of the responses.
        '''
        if regex is None:
            return self.servers[self.using].arbitrary(command)
        else:
            #===================================================================
            # https://docs.python.org/2/library/itertools.html#itertools.chain
            # 
            # "Make an iterator that returns elements from the first iterable until it is exhausted,
            # then proceeds to the next iterable, until all of the iterables are exhausted."
            # 
            # The use here is to make sure that one coherent iterable is returned in both cases.
            #===================================================================
            return chain(*[self.servers[server].arbitrary(command) for server in self.__iter__() if match(regex, server)])