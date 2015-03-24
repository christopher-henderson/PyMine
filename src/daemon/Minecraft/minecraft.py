from __future__ import absolute_import
import subprocess
import psutil
from shlex import split
from os import chdir
from .stdoutStreamer import StdoutStreamer
from functools import wraps

def EnforceStatus(desiredStatus=None, msg=''):
    def wrapper(function):
        @wraps(function)
        def decorator(self, *args, **kwargs):
            '''
            If the desired status is not met, then return msg to
            the service module and do not execute the called method.
            Else execute the called method.
            '''
            if desiredStatus is self.serverStatus():
                return function(self, *args, **kwargs)
            else:
                return (msg,)
        return decorator
    return wrapper

def ManageStdout(MaxAttempts=50):
    def wrapper(function):
        @wraps(function)
        def decorator(self, *args, **kwargs):
            '''
            Decorated methods automatically flush the stale content
            of Minecraft's stdout, performs their duties, and returns
            Minecraft's response as a generator from StdoutStreamer.retrieve.
            '''
            self.stdout.flush()
            function(self, *args, **kwargs)
            return self.stdout.retrieve(MaxAttempts=MaxAttempts)
        return decorator
    return wrapper

class Minecraft(object):

    def __init__(self, config):
        self.directory = config.get('WORLD_DIR')
        self.cmd = split(config.get('JAVA'))
        self.cmd.insert(0, 'java')
        self.server = None
        self.stdout = StdoutStreamer()

    def serverStatus(self):
        '''Returns a boolean of the status of the Minecraft server.'''
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

    @EnforceStatus(desiredStatus=False, msg='The Minecraft server is running.')
    @ManageStdout(MaxAttempts=500)
    def start(self):
        chdir(self.directory)
        self.server = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, bufsize=1)
        self.stdout = StdoutStreamer(stdout=self.server.stdout)
        self.stdout.startStreamer()

    @EnforceStatus(desiredStatus=True, msg='The Minecraft server is stopped.')
    @ManageStdout(MaxAttempts=500)
    def stop(self):
        self.server.stdin.write('stop\n')
        self.server.wait()

    def restart(self):
        yield self.stop()
        yield self.start()

    @EnforceStatus(desiredStatus=True, msg='The Minecraft server is stopped.')
    @ManageStdout()
    def arbitrary(self, command):
        '''Passes the raw command to Minecraft.'''
        self.server.stdin.write('{COMMAND}\n'.format(COMMAND=command))