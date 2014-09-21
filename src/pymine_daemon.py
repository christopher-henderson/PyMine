#!/usr/bin/env python
from __future__ import absolute_import
from Daemon.Utilities.daemonize import Daemonize
from Daemon.serverInterface import ServerInterface
from Daemon.Utilities.bindToSocket import BindToSocket
from Daemon.communicator import Communicator
import Common.PyMineExceptions as PyMineExceptions

@Daemonize
def main():
    socket = BindToSocket()
    command = socket.recv(1024)
    with ServerInterface() as multicaster:
        communicator = Communicator(multicaster, socket)
        while command != 'exit':
            communicator.execute(command)
            command = socket.recv(1024)

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