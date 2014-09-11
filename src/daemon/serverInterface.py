from src.daemon.minecraftHandler import Minecraft
import src.Utilities.PyMineExceptions as PyMineExceptions

class ServerInterface(object):
    
    def __init__(self, **kwargs):
        self.servers = {serverName: Minecraft(javaArgs) for serverName,javaArgs in kwargs.items()}
        self.using = None

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

    def forwardCommand(self, command):
        if command == 'start':
            self.servers[self.using].start()
        if command == 'stop':
            self.servers[self.using].stop()
        if command == 'restart':
            self.servers[self.using].stop()
            self.servers[self.using].start()
        else:
            self.servers[self.using].arbitrary(command)