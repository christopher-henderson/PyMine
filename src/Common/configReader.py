from yaml import load
from os.path import dirname
from pwd import getpwnam

class ConfigReader(object):

    def __init__(self):
        #=======================================================================
        # Ugh, this is starting at this class in Utilities and moving up
        # several directories until we get to the PyMine home. From there
        # we can find etc/pymine.yaml.
        #=======================================================================
        home = dirname(dirname(dirname(__file__)))
        config = '{HOME}/etc/pymine.yaml'.format(HOME=home)
        self.loadConfig(config)

    def __iter__(self):
        for section in self.config:
            yield self.config[section]

    def loadConfig(self, config):
        with open(config) as conf:
            self.config = load(conf)

    def getConfig(self):
        return self.config

    def getDefault(self):
        for section in self.config.get('servers'):
            if self.config['servers'][section].get('DEFAULT'):
                return section

    def getMinecraftConfig(self):
        return {server:config for server,config in self.config.get('servers').items()}

    def getUID(self):
        return getpwnam(self.config.get('USER')).pw_uid

    def getGID(self):
        return getpwnam(self.config.get('USER')).pw_gid

    def getPIDFile(self):
        return self.config.get('PIDFILE')

    def getSocket(self):
        return self.config.get('UNIX_SOCKET')

    def getUmask(self):
        return self.config.get('UMASK')