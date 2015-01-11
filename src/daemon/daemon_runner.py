#!/usr/bin/env python
from __future__ import absolute_import
from .DaemonTools import Daemonize
from .DaemonTools import BindToSocket
from .Management import Dispatcher


def responseClosure(connection):
    #===========================================================================
    # The purpose of this recursion is that if a command was sent
    # to a single Minecraft server then we will receive back a list
    # of strings. However, if the user provided a regex for broadcasting
    # a command to multiple Minecrafter servers then we will receive an
    # itertools.chain object containing generators which themselves contain strings.
    #===========================================================================
    def responseWrapper(iterable):
        from src.debug import say
        say(iterable.__dict__['__next__'])
        for item in iterable:
            if isinstance(item, str):
                connection.send(item)
                connection.recv(1024) # Receive ACK
                say('ack')
            else:
                responseWrapper(item)
        connection.send("EOF")
        say('EOFed')
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
            while command != 'exit' and not kill(command):
                respondWith(dispatcher.execute(command))
                command = connection.recv(1024)
            connection.close()


#===============================================================================
# @Daemonize
# def main():
#     socket = BindToSocket()
#     respondWith = responseClosure(socket)
#     command = socket.recv(1024)
#     with Dispatcher() as dispatcher:
#         for i in xrange(5):
#             for j in dispatcher.execute(command):
#                 print (j)
#===============================================================================

#===============================================================================
# def test():
#     from time import sleep
#     socket = BindToSocket()
#     with ServerInterface() as multicaster:
#         communicator = Communicator(multicaster, socket)
#         for i in xrange(5):
#             communicator.execute("restart > all")
#             sleep(2)
# test()
#===============================================================================