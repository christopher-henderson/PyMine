#!/usr/bin/env python
from Daemon.serverInterface import ServerInterface
from Daemon.daemonize import Daemonize
from Daemon.bindToSocket import BindToSocket
from Daemon.communicator import Communicator
import Utilities.PyMineExceptions as PyMineExceptions

@Daemonize
def main():
    socket = BindToSocket()
    command = socket.recv(1024)
    with ServerInterface() as multicaster:
        communicator = Communicator(multicaster, socket)
        while command != 'exit':
            communicator.execute(command)
        command = socket.recv(1024)