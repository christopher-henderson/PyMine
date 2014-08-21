from __future__ import absolute_import
import sys
import os
from daemon_classes.minecraft import Minecraft
from tools.decorators import (Daemonize, BindToSocket)

minecraft = sys.argv[1]
pidfile = sys.argv[2]
socketFile = sys.argv[3]
min_mem = sys.argv[4]
max_mem = sys.argv[5]
uid = sys.argv[6]
gid = sys.argv[7]
home = os.path.dirname(minecraft)

@Daemonize(uid, gid, pidfile, home, 0o002)
@BindToSocket(socketFile)
def mainloop(sock):
    cmd = ['java',
           '-Xmx{MAX}'.format(MAX=max_mem),
           '-Xms{MIN}'.format(MIN=min_mem),
           '-jar',
           '{PATH}'.format(PATH=minecraft),
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

mainloop()