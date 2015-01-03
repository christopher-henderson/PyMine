from __future__ import absolute_import
from re import match, error
from itertools import chain
from src.daemon.minecraftHandler import Minecraft
from src.common.configReader import ConfigReader
from src import PyMineExceptions

class ServerInterface(object):
    
    def __init__(self):
        self.config = ConfigReader()
        self.servers = {serverName: Minecraft(config) for serverName,config in self.config.getMinecraftConfig().items()}
        self.using = self.config.getDefault()

    def __iter__(self):
        for server in sorted(self.servers):
            yield server

    def __enter__(self):
        for response in self.startServer(pattern='.*'):
            #===================================================================
            # It is necessary to iterate over the returned
            # generator, otherwise self is returned immediately
            # despite the startup process being incomplete.
            #===================================================================
            pass
        return self

    def __exit__(self, type, value, traceback):
        self.stopServer(pattern='.*')

    def addServer(self, javaArgs, pattern=None):
        '''
        Adds the specified Minecraft server to the currently running
        instance of PyMine. The new Minecraft server is not automatically
        started.
        
        Raises PyMineExceptions.DuplicateMinecraftServer if there already
        exists a Minecraft server by that name.
        '''
        if pattern not in self.servers:
            self.servers[pattern] = Minecraft(javaArgs)
        else:
            raise PyMineExceptions.DuplicateMinecraftServer(pattern)

    def removeServer(self, pattern=None):
        '''
        Cleanly stops and removes the specified Minecraft server from
        the currently running instance of PyMine.
        
        Raises PyMineExceptions.NoSuchMinecraftServer if the name of
        the Minecraft server could not be found.
        '''
        if pattern in self.servers:
            self.servers[pattern].stop()
            del self.servers[pattern]
        else:
            raise PyMineExceptions.NoSuchMinecraftServer(pattern)
    
    def useServer(self, pattern=None):
        '''
        Changes the interface to handling the specified Minecraft server.
        
        Raises PyMineExceptions.NoSuchMinecraftServer if the name of
        the Minecraft server could not be found.
        '''
        if pattern in self.servers:
            self.using = pattern
        else:
            raise PyMineExceptions.NoSuchMinecraftServer(pattern)
        return ['PyMine: Using {NAME}'.format(NAME=pattern)]

    #===========================================================================
    # @TODO Issue #9.
    # These need decorators/closures/SOMETHING. Too much repetition.
    #
    # How do I capture the regex in the dec/clos?
    # ...could tweak the SelfAwareDecorator
    #===========================================================================

    def startServer(self, pattern=None):
        '''
        Default behavior to is to start the currently selected Minecraft
        server.
        
        If a regular expression is given then all servers whose name matches
        the regular expression will be started.

        Returns a generator of the responses.
        '''
        if pattern is None:
            return self.servers[self.using].start()
        else:
            #===================================================================
            # https://docs.python.org/2/library/itertools.html#itertools.chain
            # 
            # "Make an iterator that returns elements from the first iterable until it is exhausted,
            # then proceeds to the next iterable, until all of the iterables are exhausted."
            # 
            # The use here is to make sure that one coherent iterable is returned in both cases.
            #===================================================================
            try:
                return chain(*[self.servers[server].start() for server in self if match(pattern, server)])
            except error as e:
                raise PyMineExceptions.InvalidRegularExpression(pattern, e)

    def stopServer(self, pattern=None):
        '''
        Default behavior to is to stop the currently selected Minecraft
        server.

        If a regular expression is given then all servers whose name matches
        the regular expression will be stopped.

        Returns a generator of the responses.
        '''
        if pattern is None:
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
            try:
                return chain(*[self.servers[server].stop() for server in self if match(pattern, server)])
            except error as e:
                raise PyMineExceptions.InvalidRegularExpression(pattern, e)

    def restartServer(self, pattern=None):
        '''
        Default behavior to is to restart the currently selected Minecraft
        server.
        
        If a regular expression is given then all servers whose name matches
        the regular expression will be stopped.
        
        Stopping and starting each server MUST be distinct steps, as such
        this method returns a generator/itertools.chain object that itself
        contains two generators for the stop/start responses. That is, without a restart
        method you would need something like this:
        
        for response in stop():
            print (response)
        for response in start():
            print (response)
            
        With this restart method you still need two 'for' loops, but instead they
        are nested, like so:
        
        for stopStart in restart():
            for response in stopStart:
                print (response)
        '''
        if pattern is None:
            return self.servers[self.using].restart()
        else:
            #===================================================================
            # https://docs.python.org/2/library/itertools.html#itertools.chain
            # 
            # "Make an iterator that returns elements from the first iterable until it is exhausted,
            # then proceeds to the next iterable, until all of the iterables are exhausted."
            # 
            # The use here is to make sure that one coherent iterable is returned in both cases.
            #===================================================================
            try:
                return chain(*[self.servers[server].restart() for server in self if match(pattern, server)])
            except error as e:
                raise PyMineExceptions.InvalidRegularExpression(pattern, e)

    def forwardCommand(self, command, pattern=None):
        '''
        Default behavior to is to forward a command to the currently selected Minecraft
        server.
        
        If a regular expression is given then all servers whose name matches
        the regular expression will be passed the command.
        
        Returns a generator of the responses.
        '''
        if pattern is None:
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
            try:
                return chain(*[self.servers[server].arbitrary(command) for server in self if match(pattern, server)])
            except error as e:
                raise PyMineExceptions.InvalidRegularExpression(pattern, e)