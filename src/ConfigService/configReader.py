from __future__ import absolute_import
from functools import wraps
from yaml import load
from os.path import dirname
from pwd import getpwnam

def LazyLoad(function):
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        if not self.config:
            self.loadConfig()
        return function(self, *args, **kwargs)
    return wrapper

class ConfigReader(object):

    def __init__(self):
        #=======================================================================
        # Ugh, this is starting at this class in Utilities and moving up
        # several directories until we get to the PyMine home. From there
        # we can find etc/pymine.yaml.
        #=======================================================================
        home = dirname(dirname(dirname(__file__)))
        self.configFile = '{HOME}/etc/pymine.yaml'.format(HOME=home)
        self.config = None

    def __iter__(self):
        for section in self.config:
            yield self.config[section]

    def loadConfig(self):
        with open(self.configFile) as conf:
            self.config = load(conf)

    @LazyLoad()
    def getConfig(self):
        return self.config

    @LazyLoad()
    def getDefault(self):
        for section in self.config.get('servers'):
            if self.config['servers'][section].get('DEFAULT'):
                return section

    @LazyLoad()
    def getMinecraftConfig(self):
        return {server:config for server,config in self.config.get('servers').items()}

    @LazyLoad()
    def getUID(self):
        return getpwnam(self.config.get('USER')).pw_uid

    @LazyLoad()
    def getGID(self):
        return getpwnam(self.config.get('USER')).pw_gid

    @LazyLoad()
    def getPIDFile(self):
        return self.config.get('PIDFILE')

    @LazyLoad()
    def getSocket(self):
        return self.config.get('UNIX_SOCKET')

    @LazyLoad()
    def getUmask(self):
        return self.config.get('UMASK')