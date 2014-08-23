import os
from config import *
from classes.minecraft import Minecraft
from decorators import (Daemonize, BindToSocket)

home = os.path.dirname(MINECRAFT)

@Daemonize(UID, GID, PIDFILE, home, 0o002)
@BindToSocket(UNIX_SOCKET)
def main(sock):
    cmd = ['java',
           '-Xmx{MAX}'.format(MAX=JAVA_MAX_MEMORY),
           '-Xms{MIN}'.format(MIN=JAVA_MIN_MEMORY),
           '-jar',
           '{PATH}'.format(PATH=MINECRAFT),
           'nogui'
           ]
    server = Minecraft(cmd)
    killSignal = False
    while not killSignal:
        #=======================================================================
        # This connection assignment is blocking.
        # It is effectively what causes the daemon to
        # go to sleep while a user is not interacting
        # with the server.
        #=======================================================================
        connection, address = sock.accept()
        command = connection.recv(1024)
        while command:
            if command == 'start':
                response = server.start()
            elif command == 'stop':
                response = server.stop()
                for line in response:
                    connection.send(line)
                    connection.recv(1024)
                connection.send("EOF")
                killSignal = True
                break
            elif command == 'status':
                if server.running():
                    response = ['The Minecraft server is running.']
                else:
                    response ['The Minecraft server is stopped.']
            else:
                response = server.arbitrary(command)
            for line in response:
                connection.send(line)
                connection.recv(1024)
            connection.send("EOF")
            command = connection.recv(1024)
        connection.close()

main()