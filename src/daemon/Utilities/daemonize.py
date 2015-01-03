from __future__ import absolute_import
from functools import wraps
from src.common import Config
import daemon
import daemon.pidfile

def Daemonize(function):
    '''
    Decorates a function that will be ran as a well behaved Unix daemon.
    '''
    @wraps(function)
    def wrapper(*args, **kwargs):
        context = daemon.DaemonContext(
            working_directory = '/',
            uid = Config.getUID(),
            gid = Config.getGID(),
            pidfile=daemon.pidfile.PIDLockFile(Config.getPIDFile())
            )
        if Config.getUmask() is not None:
            context.umask = Config.getUmask()
        with context:
            function(*args, **kwargs)
    return wrapper