import socket
import os
import pwd
import sys
import psutil
import subprocess
import tarfile
from time import time, strftime
SOCKET_TIMEOUT = 30

class DaemonHandler:
    
    def __init__(self, SCRIPT_HOME, MINECRAFT, PIDFILE, UNIX_SOCKET, MIN_MEMORY, MAX_MEMORY, USER, BACKUP):
        self.scriptHome = SCRIPT_HOME
        self.backupDir = os.path.expanduser(BACKUP)
        self.minecraft = os.path.expanduser(MINECRAFT)
        self.pidfile = os.path.expanduser(PIDFILE)
        self.min_memory = os.path.expanduser(MIN_MEMORY)
        self.max_memory = os.path.expanduser(MAX_MEMORY)
        self.unix_socket = os.path.expanduser(UNIX_SOCKET)
        self.socketHome = os.path.dirname(UNIX_SOCKET)
        self.pidHome = os.path.dirname(PIDFILE)
        self.uid,self.gid = self._getIDs(USER)
        self.pid = self._getPID()
        self.sock = None
        if self._isRunning():
            self._connectToSocket()

    def _getIDs(self, user):
        #=======================================================================
        # Does our user exist? **EXIT POINT**
        #=======================================================================
        try:
            uid = pwd.getpwnam(user).pw_uid
            gid = pwd.getpwnam(user).pw_gid
        except KeyError as error:
            print (error)
            sys.exit(1)
        return uid,gid

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

    def _ensureMinecraft(self):
        #=======================================================================
        # Does Minecraft exist? **EXIT POINT**
        #=======================================================================
        minecraftHome = os.path.split(self.minecraft)[0]
        try:
            homeStats = os.stat(minecraftHome)
        except (IOError, OSError) as error:
            print (error)
            sys.exit(1)
        homePermissions = int(oct(homeStats.st_mode))
        homeUserOwned = self.uid == homeStats.st_uid and homePermissions % 1000 >= 600
        homeGroupOwned = self.gid == homeStats.st_gid and homePermissions % 100 >= 60
        homeWorldOwned = homePermissions % 10 >= 6
        if not homeUserOwned and not homeGroupOwned and not homeWorldOwned:
            print ('Permission denied: {PATH}'.format(PATH=minecraftHome))
            sys.exit(1)
        try:
            jarStats = os.stat(self.minecraft)
        except (IOError, OSError) as error:
            print (error)
            sys.exit(1)
        jarPermissions = int(oct(jarStats.st_mode))
        jarUserOwned = self.uid == jarStats.st_uid and jarPermissions % 1000 >= 400
        jarGroupOwned = self.gid == jarStats.st_gid and jarPermissions % 100 >= 40
        jarWorldOwned = jarPermissions % 10 >= 4
        if not jarUserOwned and not jarGroupOwned and not jarWorldOwned:
            print ('Permission denied: {PATH}'.format(PATH=self.minecraft))
            sys.exit(1)

    def _ensurePIDHome(self):
        #=======================================================================
        # Does our PID file directory exist? If not, make it.
        #=======================================================================
        try:
            os.stat(self.pidHome)
        except:
            os.mkdir(self.pidHome, 0750)
            os.chown(self.pidHome, self.uid, self.gid)
            
    def _ensureSocketHome(self):
        #=======================================================================
        # Does our socket directory exist? If not, make it.
        #=======================================================================
        try:
            os.stat(self.socketHome)
        except:
            os.mkdir(self.socketHome, 0750)
            os.chown(self.socketHome, self.uid, self.gid)

    def _ensureBackupDir(self):
        #=======================================================================
        # Does our backup directory exists?
        #=======================================================================
        try:
            os.stat(self.backupDir)
        except (IOError, OSError) as error:
            print (error)
            sys.exit(1)

    def _startDaemon(self):
        self._ensureMinecraft()
        self._ensurePIDHome()
        self._ensureSocketHome()
        self.pid = self._getPID()
        if self.pid is not 0:
            os.remove(self.pidfile)
            #===========================================================
            # That is, we retrieved a PID but there's nothing there.
            # Since you can't handle a SIGKILL this will happen if
            # you kill -9, so now we have to clean up the orphaned pidfile.
            #===========================================================
        subprocess.Popen(['python', 'bin/pymineDaemon.py'.format(PATH=self.scriptHome), self.minecraft, self.pidfile, self.unix_socket, self.min_memory, self.max_memory, str(self.uid), str(self.gid)], close_fds=True, bufsize=1)
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
                print ('An error occurred while starting the pymine daemon.')
        else:
            #===============================================================
            # The pymine_daemon is running and we are connected, now we need to ask the pymine_daemon
            # if Minecraft itself is running. If not, start it up.
            #===============================================================
            #self.sock.send('status')
            #isRunning = loads(self.sock.recv(1024))
            #if not isRunning:
            self.sock.send('start')
            self._getResponse()
            #else:
            #    print ('The PyMine daemon is already running.')

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
        self._ensureBackupDir()
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
        elif command and running:
            self.sock.send(command)
            self._getResponse()
        elif command:
            print ('Invalid command.')