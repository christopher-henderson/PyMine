from functools import wraps
from sys import argv

def ParseArgs(function):
    '''
    If the length of sys.argv is less then two then no arguments were
    given and we will interpret that as wanting to go into "interactive"
    mode. Else, parse the arguments given. start/stop/restart are captured
    by the serviceHandler class, anything else is passed onto Minecraft raw.
    '''
    @wraps(function)
    def decorator(*args, **kwargs):
        interactive = False
        arguments = []
        if len(argv) < 2:
            interactive = True
        else:
            arguments = argv[1]
            for arg in argv[2:]:
                arguments = '{BASE} {ARG}'.format(BASE=arguments, ARG=arg)
        function(interactive, arguments)
    return decorator