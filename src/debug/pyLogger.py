from __future__ import absolute_import
from os.path import dirname
import logging

class Logger(object):
    
    logger = logging.getLogger('pymine')
    logger.setLevel('DEBUG')
    fileHandler = logging.FileHandler('{PATH}/logs/pymine.log'.format(PATH=dirname(dirname(dirname(__file__)))))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    fileno = fileHandler.stream.fileno()

    @classmethod
    def debug(cls, message):
        cls.logger.debug(message)
        
    @classmethod
    def info(cls, message):
        cls.logger.info(message)
        
    @classmethod
    def warning(cls, message):
        cls.logger.warning(message)
   
    @classmethod
    def critical(cls, message):
        cls.logger.critical(message)