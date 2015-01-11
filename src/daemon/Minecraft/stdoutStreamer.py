from __future__ import absolute_import
from src.tools import Threaded
from re import sub
from time import sleep
try:
    #===========================================================================
    # Python 2
    #===========================================================================
    from Queue import Queue, Full, Empty
except ImportError:
    #===========================================================================
    # Python 3
    #===========================================================================
    from queue import Queue, Full, Empty

class StdoutStreamer(object):

    def __init__(self, stdout=None):
        self.queue = Queue()
        self.stdout = stdout

    @Threaded
    def startStreamer(self):
        '''Starts this StdoutStreamer's reader.'''
        for line in iter(self.stdout.readline, b''):
            try:
                self.queue.put(line)
            except Full:
                self.queue.get_nowait()
                self.queue.put(line)

    def flush(self):
        '''Flush the StdoutStreamer'''
        #=======================================================================
        # The queue is likely to have a bunch of history
        # in it that we need to flush before we run a command.
        #=======================================================================
        while not self.queue.empty():
            self.queue.get_nowait()

    def retrieve(self, pollingPeriod=0.001, MaxAttempts=50):
        '''Retrieves a generator of the Minecraft's current stdout content.'''
        #=======================================================================
        # This is essentially a do-while, the point being that this Python should wait for Minecraft
        # to start reporting back before the attempts counter starts to increment.
        #=======================================================================
        yield sub('\n', '', self.queue.get())
        attempts = 0
        while attempts <= MaxAttempts:
            #===================================================================
            # @TODO This pollingPeriod/MaxAttemps thing should really be in the config file since it can easily be tuned
            # depending on the machine this is running on. Put it under a "Don't
            # touch unless you know what you're doing" section.
            #
            # Minecraft really has no idea that this Python is controlling it. As such, it
            # doesn't do nice things like send STOP signals for output, leading to this code
            # not really being able to tell when Minecraft is done talking. How I got around this
            # was to repeatedly attempt to retrieve from the stdout queue at a reduced frequency
            # (set to 1kHz). Once MaxAttempts of consecutive Queue.Empty exceptions are hit we give up
            # and conclude that Minecraft has gone silent.
            #
            # If you know of a better way then please contact me at chris@chenderson.org.
            #===================================================================
            sleep(pollingPeriod)
            try:
                yield sub('\n', '', self.queue.get_nowait())
            except Empty:
                attempts += 1