import socket
import os
import psutil
import subprocess
import tarfile
from time import time, strftime
from bin.config import *
from data.license import printLicense
from data.help import printHelp
from data.copyright import printCopyright
SOCKET_TIMEOUT = 30

class DaemonHandler:

    def __init__(self):
        validateConfig()
        self.scriptHome = BIN
        self.backupDir = BACKUP_DIR
        self.minecraft = MINECRAFT
        self.pidfile = PIDFILE
        self.min_memory = JAVA_MIN_MEMORY
        self.max_memory = JAVA_MAX_MEMORY
        self.unix_socket = UNIX_SOCKET
        self.socketHome = SOCKET_HOME
        self.pidHome = PIDFILE_HOME
        self.uid = UID
        self.gid = GID
        self.pid = self._getPID()
        self.sock = None
        if self._isRunning():
            self._connectToSocket()

    def _getPID(self):
        try:
            with open(self.pidfile) as pidfile:
                pid = int(pidfile.readline())
        except IOError:
            pid = 0
        return pid

    def _isRunning(self):
        try:
            psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            isRunning = False
        else:
            isRunning = True
        return isRunning

    def _connectToSocket(self):
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
            print ('Timed out trying to communicate with the PyMine pymine_daemon.')

    def _startDaemon(self):
        self.pid = self._getPID()
        if self.pid is not 0:
            os.remove(self.pidfile)
            #===========================================================
            # That is, we retrieved a PID but there's nothing there.
            # Since you can't handle a SIGKILL this will happen if
            # you kill -9, so now we have to clean up the orphaned pidfile.
            #===========================================================
        subprocess.Popen(['python', '{PATH}/pymineDaemon.py'.format(PATH=self.scriptHome)], close_fds=True, bufsize=1)
        self._connectToSocket()
        self.pid = self._getPID()

    def _getResponse(self):
        response = self.sock.recv(1024)
        while response != "EOF":
            print (response)
            self.sock.send('Continue')
            response = self.sock.recv(1024)

    def _start(self, running):
        if not running:
            #===============================================================
            # The pymine_daemon is down and we are not connected. We are clear
            # to do a clean startup of the pymine_daemon and Minecraft process.
            #===============================================================
            self._startDaemon()
            running = self._isRunning()
            if running:
                self.sock.send('start')
                self._getResponse()
            else:
                print ('An error occurred while starting the Pymine daemon.')
        else:
            #===============================================================
            # The pymine_daemon is running and we are connected, now we need to ask the pymine_daemon
            # if Minecraft itself is running. If not, start it up.
            #===============================================================
            self.sock.send('start')
            self._getResponse()

    def _stop(self, running):
        if running:
            self.sock.send('stop')
            self._getResponse()
            self.sock.close()
        else:
            print ('The PyMine daemon is not running.')

    def _waitForCleanup(self):
        exists = True
        start = time()
        timer = time() - start
        while exists and timer < 30:
            exists = self._isRunning()
            timer = time() - start
        if exists:
            print ('Failed to stop the PyMine daemon.')

    def _restart(self, running):
        self._stop(running)
        self._waitForCleanup()
        running = self._isRunning()
        self._start(running)

    def _status(self, running):
        if running:
            self.sock.send('status')
            self._getResponse()
        else:
            print ('The PyMine daemon is stopped.')

    def _backup(self, running):
        originalPath = '{BASE}/world'.format(BASE=os.path.split(self.minecraft)[0])
        date = strftime("%Y-%m-%d-%H.%M.%S%p")
        backupPath = '{BASE}/world_{DATE}.tar.gz'.format(BASE=self.backupDir, DATE=date)
        with tarfile.TarFile.open(backupPath, 'w|gz') as backup:
            backup.add(originalPath, arcname='world')
        os.chown(backupPath, self.uid, self.gid)
        if running:
            self.sock.send('say PyMine has made a world backup.')
            self._getResponse()
        else:
            print ('PyMine has made a world backup.')

    def runCommand(self, command):
        running = self._isRunning()
        if command == 'start':
            self._start(running)
        elif command == 'stop':
            self._stop(running)
        elif command == 'restart':
            self._restart(running)
        elif command == 'status':
            self._status(running)
        elif command == 'backup':
            self._backup(running)
        elif command == ('license'):
            printLicense()
        elif command == ('pmhelp'):
            printHelp()
        elif command == ('copyright'):
            printCopyright()
        elif command and running:
            self.sock.send(command)
            self._getResponse()
        elif command:
            print ('Invalid command.\nType "pmhelp" for help.')