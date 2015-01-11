def say(thing):
    with open('/home/chris/pymine/debug', 'a+') as debug:
        debug.write(thing)