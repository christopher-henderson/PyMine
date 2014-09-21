from __future__ import absolute_import
from functools import wraps
from Common.configReader import ConfigReader
import daemon
import daemon.pidfile

def Daemonize(function):
    '''
    Decorates a function that will be ran as a well behaved Unix daemon.
    '''
    @wraps(function)
    def wrapper(*args, **kwargs):
        config = ConfigReader()
        context = daemon.DaemonContext(
            working_directory = '/',
            uid = config.getUID(),
            gid = config.getGID(),
            pidfile=daemon.pidfile.PIDLockFile(config.getPIDFile())
            )
        if config.getUmask() is not None:
            context.umask = config.getUmask()
        del config
        with context:
            function(*args, **kwargs)
    return wrapper