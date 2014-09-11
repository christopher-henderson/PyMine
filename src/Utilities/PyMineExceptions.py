class PyMineException(Exception):
    pass

class NoSuchMinecraftServer(PyMineException):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Minecraft server could not be found: {NAME}".format(NAME=self.name)

class DuplicateMinecraftServer(PyMineException):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Minecraft server already exists: {NAME}".format(NAME=self.name)
