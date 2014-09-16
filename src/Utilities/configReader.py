from yaml import load
from os.path import dirname

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

    def getDaemonConfig(self):
        return {section:config for section,config in self.config.items() if section != 'servers'}


