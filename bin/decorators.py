from functools import wraps
import os
import sys
import socket
import daemon
import daemon.pidfile
import threading

def SelfAwareDecorator(outerFunction):
    '''
    The decorated class method itself becomes a decorator
    that is aware of the class instance's methods and attributes.
    The second parameter after self must be the function you are
    ultimately decorating.

    Usage:

    @SelfAwareDecorator
    def StatusCheck(self, function, desiredStatus, ErrorMsg='Error'):
        if desiredStatus is self.status():
            function()
        else:
            print (ErrorMsg)

    @StatusCheck(False, ErrorMsg='The server is already running!')
    def start()
        self.server.start()

    It is also possible to "finish" giving arguments to the decorated
    function from within the self aware decorator.
    '''
    @wraps(outerFunction)
    def decorator(*decArgs, **decKwargs):
        def wrapper(innerFunction):
            @wraps(innerFunction)
            def inner(self, *funcArgs, **funcKwargs):
                @wraps(innerFunction)
                def f(*innerArgs, **innerKwargs):
                    #===========================================================
                    # We wrap the innerFunction one last time so that we can
                    # pass supplemental arguments while in the decorating method.
                    # It also allows us to make reference to the innerFunction's
                    # attributes (i.e. func_name, doc string, etc.) while in the
                    # decorator (these things are lost when using functools.partial).
                    # Plus it is much more helpful to see the proper traceback if you do
                    # something bad with the innerFunction while in the decorator. 
                    #===========================================================
                    finalArgs = innerArgs + funcArgs
                    finalKwargs = dict(innerKwargs.items() + funcKwargs.items())
                    return innerFunction(self, *finalArgs, **finalKwargs)
                return outerFunction(self, f, *decArgs, **decKwargs)
            return inner
        return wrapper
    return decorator

def Threadify(function):
    '''
    Every call of the decorated function will spawn a
    daemonized thread. Returns a threading.Thread object.
    '''
    @wraps(function)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=function, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper

def ParseArgs(function):
    '''
    If the length of sys.argv is less then two then no arguments were
    given and we will interpret that is wanting to go into "interactive"
    mode. Else, parse the arguments given. start/stop/restart are captured
    by the serviceHandler class, anything else is passed onto Minecraft raw.
    '''
    @wraps(function)
    def decorator(*args, **kwargs):
        interactive = False
        arguments = []
        if len(sys.argv) < 2:
            interactive = True
        else:
            arguments = sys.argv[1]
            for arg in sys.argv[2:]:
                arguments = '{BASE} {ARG}'.format(BASE=arguments, ARG=arg)
        function(interactive, arguments)
    return decorator

def BindToSocket(SOCKET):
    '''
    Binds to the provided socket path. Returns a 
    socket.socket object to the decorated function.
    '''
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                os.stat(SOCKET)
            except:
                pass
            else:
                os.remove(SOCKET)
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(SOCKET)
            sock.listen(1)
            function(sock)
        return wrapper
    return decorator

def Daemonize(uid, gid, pidfile, home, umask, files_preserve=None):
    '''
    Decorates a function that will be ran as a well behaved Unix daemon.
    '''
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            context = daemon.DaemonContext(
                working_directory = home,
                umask = umask,
                uid = int(uid),
                gid = int(gid),
                pidfile=daemon.pidfile.PIDLockFile(pidfile)
                )
            if files_preserve:
                context.files_preserve = files_preserve
            with context:
                function(*args, **kwargs)
        return wrapper
    return decorator
