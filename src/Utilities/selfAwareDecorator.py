from functools import wraps

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