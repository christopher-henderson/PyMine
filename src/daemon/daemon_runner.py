from __future__ import absolute_import
from .DaemonTools import Daemonize
from .DaemonTools import BindToSocket
from .Management import Dispatcher
from src.debug import Logger


def responseClosure(connection):
    #===========================================================================
    # The purpose of this recursion is that if a command was sent
    # to a single Minecraft server then we will receive back a generator
    # of strings. However, if the user provided a regex for broadcasting
    # a command to multiple Minecrafter servers then we will receive an
    # itertools.chain object containing generators which themselves contain strings.
    #
    # This marches down the chain of iterables until a collection of strings is reached.
    #===========================================================================
    def responseWrapper(iterable):
        for item in iterable:
            if isinstance(item, str):
                connection.send(item)
                connection.recv(1024) # Receive ACK
            else:
                responseWrapper(item)
        connection.send("EOF")
    return responseWrapper

@Daemonize
def main():
    socket = BindToSocket()
    kill = lambda cmd: cmd == 'kill'
    command = None
    with Dispatcher() as dispatcher:
        while not kill(command):
            connection, address = socket.accept()
            respondWith = responseClosure(connection)
            command = connection.recv(1024)
            while command and not kill(command):
                respondWith(dispatcher.execute(command))
                command = connection.recv(1024)
            connection.close()