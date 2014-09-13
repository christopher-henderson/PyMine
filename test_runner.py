#/usr/bin/env python
from src.Daemon.serverInterface import ServerInterface
import shlex

command1 = shlex.split('java -Xmx1G -Xms1G -jar /opt/minecraft/minecraft.jar nogui')
command2 = shlex.split('java -Xmx1G -Xms1G -jar /opt/minecraft2/minecraft.jar nogui')

minecrafts = {'default': command1,
              'cool_server': command2
              }

#===============================================================================
# server = ServerInterface(**minecrafts)
# response = server.startServer(regex='.*')
# for i in response:
#     print i
# 
# for response in server.restartServer(regex='.*'):
#     for i in response:
#         print i
#===============================================================================
with ServerInterface(**minecrafts) as multicaster:
    for response in multicaster.forwardCommand('help'):
        print response
