import subprocess
import psutil
from time import sleep
from re import sub
from decorators import (Threadify, SelfAwareDecorator)
try:
    import Queue
except ImportError:
    import queue as Queue

class Minecraft:

    def __init__(self, java_args):
        self.cmd = java_args
        self.server = None
        self.queue = Queue.Queue()
        self.stdoutThread = None

    @Threadify
    def _enqueueStdout(self, stdout=None):
        for line in iter(stdout.readline, b''):
            try:
                self.queue.put(line)
            except Queue.Full:
                self.queue.get_nowait()
                self.queue.put(line)

    @SelfAwareDecorator
    def stdout(self, function, MaxAttempts=50):
        self._flushStdout()
        function()
        return self._retrieveStdout(MaxAttempts=MaxAttempts)

    @SelfAwareDecorator
    def CheckStatus(self, function, desiredStatus=None, msg=''):
        if desiredStatus is self.running():
            #===================================================================
            # This return is ultimately the self._retrieveStdout generator.
            #===================================================================
            return function()
        else:
            return [msg]

    def running(self):
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

    def _flushStdout(self):
        #=======================================================================
        # The queue is likely to have a bunch of history
        # in it that we need to flush before we run a command.
        #=======================================================================
        while True:
            try:
                self.queue.get_nowait()
            except Queue.Empty:
                break

    def _retrieveStdout(self, pollingPeriod=0.001, MaxAttempts=50):
        while True:
            #=======================================================================
            # Knock on stdout until Minecraft starts
            # talking back. It is possible to not do this
            # and simply make the below sleep longer, but
            # in that case the sleep needs to be ~0.1 which
            # is non-trivial to a human.
            #=======================================================================
            try:
                yield sub('\n', '', self.queue.get_nowait())
            except Queue.Empty:
                pass
            else:
                break
        attempts = 0
        while True:
            #===================================================================
            # @TODO This should really be in the config file since it can easily be tuned
            # depending on the machine this is running on. Put it under a "Don't
            # touch unless you know what you're doing" section.
            #
            # Minecraft really has no idea that this Python is controlling it. As such, it
            # doesn't do nice things like send STOP signals for output, leading to this code
            # not really being able to tell when Minecraft is done talking. How I got around this
            # was to repeatedly attempt to retrieve from the stdout queue at a reduced frequency
            # (set to 1kHz). Once MaxAttempts of consecutive Queue.Empty exceptions are hit we give up
            # and conclude that Minecraft has gone silent.
            #===================================================================
            sleep(pollingPeriod)
            try:
                yield sub('\n', '', self.queue.get_nowait())
            except Queue.Empty:
                attempts += 1
                if attempts >= MaxAttempts:
                    break

    @CheckStatus(desiredStatus=False, msg='The Minecraft server is running.')
    @stdout(MaxAttempts=500)
    def start(self):
        self.server = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, bufsize=1)
        self.stdoutThread = self._enqueueStdout(stdout=self.server.stdout)

    @CheckStatus(desiredStatus=True, msg='The Minecraft server is stopped.')
    @stdout(MaxAttempts=500)
    def stop(self):
        self.server.stdin.write('stop\n')
        self.server.wait()

    @CheckStatus(desiredStatus=True, msg='The Minecraft server is stopped.')
    @stdout()
    def arbitrary(self, command):
        self.server.stdin.write('{COMMAND}\n'.format(COMMAND=command))