from Utilities.configReader import ConfigReader
from os import (stat, remove)
import socket

def BindToSocket():
    SOCKET = ConfigReader().getSocket()
    try:
        stat(SOCKET)
    except:
        pass
    else:
        remove(SOCKET)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET)
    sock.listen(1)
    return sock