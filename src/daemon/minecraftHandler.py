import subprocess
import psutil
from src.Utilities.selfAwareDecorator import SelfAwareDecorator
from src.daemon.stdoutStreamer import StdoutStreamer

class Minecraft(object):

    def __init__(self, java_args):
        self.cmd = java_args
        self.server = None
        self.stdout = StdoutStreamer()

    @SelfAwareDecorator
    def ManageStdout(self, function, MaxAttempts=50):
        self.stdout.flush()
        function()
        return self.stdout.retrieve(MaxAttempts=MaxAttempts)

    @SelfAwareDecorator
    def CheckStatus(self, function, desiredStatus=None, msg=''):
        if desiredStatus is self.getServerStatus():
            return function()
        else:
            return [msg]

    def getServerStatus(self):
        try:
            zombie = psutil.Process(self.server.pid).status()
        except (psutil.NoSuchProcess, AttributeError):
                status = False
        else:
            if zombie == psutil.STATUS_ZOMBIE:
                status = False
                #===============================================================
                # Zombifaction will happen if someone has been
                # sending SIGTERM to Minecraft without this daemon
                # knowing about it. Performing self.server.wait() will clean it
                # up for us.
                #===============================================================
                self.server.wait()
            else:
                status = True
        return status

    @CheckStatus(desiredStatus=False, msg='The Minecraft server is running.')
    @ManageStdout(MaxAttempts=500)
    def start(self):
        self.server = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, bufsize=1)
        self.stdout = StdoutStreamer(stdout=self.server.stdout)
        self.stdout.startStreamer()

    @CheckStatus(desiredStatus=True, msg='The Minecraft server is stopped.')
    @ManageStdout(MaxAttempts=500)
    def stop(self):
        self.server.stdin.write('stop\n')
        self.server.wait()

    @CheckStatus(desiredStatus=True, msg='The Minecraft server is stopped.')
    @ManageStdout()
    def arbitrary(self, command):
        self.server.stdin.write('{COMMAND}\n'.format(COMMAND=command))