from functools import wraps
from threading import Thread

def Threaded(function):
    '''
    Every call of the decorated function will spawn a
    daemonized thread. Returns a threading.Thread object.
    '''
    @wraps(function)
    def wrapper(*args, **kwargs):
        thread = Thread(target=function, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper