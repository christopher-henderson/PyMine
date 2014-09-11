from src.Utilities.threadify import Threadify
from re import sub
from time import sleep
try:
    import Queue
except ImportError:
    import queue as Queue

class StdoutStreamer(object):

    def __init__(self, stdout=None):
        self.queue = Queue.Queue()
        self.stdout = stdout

    @Threadify
    def startStreamer(self):
        for line in iter(self.stdout.readline, b''):
            try:
                self.queue.put(line)
            except Queue.Full:
                self.queue.get_nowait()
                self.queue.put(line)

    def flush(self):
        #=======================================================================
        # The queue is likely to have a bunch of history
        # in it that we need to flush before we run a command.
        #=======================================================================
        while True:
            try:
                self.queue.get_nowait()
            except Queue.Empty:
                break

    def retrieve(self, pollingPeriod=0.001, MaxAttempts=50):
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