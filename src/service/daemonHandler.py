from __future__ import absolute_import
from multiprocessing import Process as multiprocess
from src.daemon.daemon_runner import main as Daemon
import socket
import os
from psutil import Process, NoSuchProcess
from subprocess import Popen
import tarfile
from src.ConfigService import Config
from time import time, strftime
from src.PrintBacks import printCopyright, printLicense, printHelp
SOCKET_TIMEOUT = 30

class DaemonHandler:

    def __init__(self):
        self.unix_socket = Config.getSocket()
        self.pidFile = Config.getPIDFile()
        self.pid = self.getDaemonPID()
        self.scriptHome = None
        self.sock = None
        if self.isRunning():
            self.connectToSocket()

    def getDaemonPID(self):
        '''Returns an integer of the PID. Returns 0 if the PID file could not be accessed.'''
        try:
            with open(self.pidFile) as pidfile:
                return int(pidfile.readline())
        except IOError:
            return 0

    def isRunning(self):
        '''Checks if the PyMine daemon is running.'''
        try:
            Process(self.pid)
        except NoSuchProcess:
            return False
        else:
            return True

    def connectToSocket(self):
        '''Connects to the PyMine daemon via Unix socket.'''
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        initConnect = False
        start = time()
        timer = 0
        while not initConnect and timer <= SOCKET_TIMEOUT:
            try:
                self.sock.connect(self.unix_socket)
            except socket.error:
                timer = time() - start
            else:
                initConnect = True
        if not initConnect:
            print ('Timed out trying to communicate with the PyMine Daemon.')

    def startDaemon(self):
        self.pid = self.getDaemonPID()
        if self.pid is not 0:
            os.remove(self.pidFile)
            #===========================================================
            # That is, we retrieved a PID but there's nothing actually
            # running at that ID.
            # Since you can't handle a SIGKILL this will happen if
            # you kill -9, so now we have to clean up the orphaned pidfile
            # before initiating startup.
            #===========================================================
        #Popen(['python', '{PATH}/pymine'.format(PATH='/home/chris/pymine'), '--daemon'], close_fds=True, bufsize=1)
        multiprocess(target=Daemon).start()
        self.connectToSocket()
        self.pid = self.getDaemonPID()

    def getResponse(self):
        response = self.sock.recv(1024)
        while response != "EOF":
            print (response)
            self.sock.send('ACK')
            response = self.sock.recv(1024)

    def start(self):
        if not self.isRunning():
            #===============================================================
            # The pymine_daemon is down and we are not connected. We are clear
            # to do a clean startup of the pymine_daemon and Minecraft process.
            #===============================================================
            self.startDaemon()
            if not self.isRunning():
                print ('An error occurred while starting the PyMine daemon.')
        else:
            print ('The PyMine daemon is already running.')

    def stop(self):
        if self.isRunning():
            self.sock.send('kill')
            self.getResponse()
            self.sock.close()
        else:
            print ('The PyMine daemon is not running.')

    def restart(self):
        self.stop()
        self.waitForCleanup()
        self.start()

    def waitForCleanup(self):
        start = time()
        timer = 0
        while self.isRunning() and timer < 30:
            timer = time() - start
        if self.isRunning():
            print ('Failed to stop the PyMine daemon.')

    def status(self):
        if self.isRunning():
            self.sock.send('status')
            self.getResponse()
        else:
            print ('The PyMine daemon is stopped.')

    #===========================================================================
    # @TODO backup responsibility needs to be shoveled off to the Minecraft class.
    # @deprecated
    #===========================================================================
    def backup(self, running):
        originalPath = '{BASE}/world'.format(BASE=os.path.split(self.minecraft)[0])
        date = strftime("%Y-%m-%d-%H.%M.%S%p")
        backupPath = '{BASE}/world_{DATE}.tar.gz'.format(BASE=self.backupDir, DATE=date)
        with tarfile.TarFile.open(backupPath, 'w|gz') as backup:
            backup.add(originalPath, arcname='world')
        os.chown(backupPath, self.uid, self.gid)
        if running:
            self.sock.send('say PyMine has made a world backup.')
            self.getResponse()
        else:
            print ('PyMine has made a world backup.')

    def runCommand(self, command):
        if command == 'start pymine':
            self.start()
        elif command == 'stop pymine':
            self.stop()
        elif command == 'restart pymine':
            self.restart()
        elif command == 'license':
            printLicense()
        elif command == 'pmhelp':
            printHelp()
        elif command == 'copyright':
            printCopyright()
        #=======================================================================
        # At this point the command appears to be for the Minecraft daemon
        # rather than the service. If the daemon isn't even running then an
        # error must be printed here.
        #=======================================================================
        elif command and self.isRunning():
            self.sock.send(command)
            self.getResponse()
        elif command:
            print ('Invalid command.\nType "pmhelp" for help.')