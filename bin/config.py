import yaml
import os
import pwd
import sys

HOME = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
with open('{HOME}/etc/pymine.yaml'.format(HOME=HOME), 'r') as conf:
    config = yaml.load(conf)

BIN = os.path.dirname(os.path.realpath(__file__))
BACKUP_DIR = os.path.expanduser(config['BACKUP_DIR'])
MINECRAFT = os.path.expanduser(config['MINECRAFT'])
PIDFILE = os.path.expanduser(config['PIDFILE'])
JAVA_MIN_MEMORY = os.path.expanduser(config['JAVA_MIN_MEMORY'])
JAVA_MAX_MEMORY = os.path.expanduser(config['JAVA_MAX_MEMORY'])
UNIX_SOCKET = os.path.expanduser(config['UNIX_SOCKET'])
SOCKET_HOME = os.path.dirname(config['UNIX_SOCKET'])
PIDFILE_HOME = os.path.dirname(config['PIDFILE'])
USER = config['USER']

UID = None
GID = None
try:
    UID = pwd.getpwnam(USER).pw_uid
    GID = pwd.getpwnam(USER).pw_gid
except KeyError as error:
    pass

def _ensureIDs():
    #=======================================================================
    # Does our user exist? **EXIT POINT**
    #=======================================================================
    error = False
    try:
        pwd.getpwnam(USER).pw_uid
        pwd.getpwnam(USER).pw_gid
    except KeyError as e:
        print (e)
        error = True
    else:
        if os.geteuid() is not 0 and UID != os.geteuid():
            print ('Unprivileged user. Either run this script as sudo or as the configured Minecraft user.')
            error = True
    return error

def _ensureDirectory(DIR):
    #=======================================================================
    # Does our directory exist? If not, try to make it.
    #=======================================================================
    error = False
    try:
        os.stat(DIR)
    except OSError:
            try:
                os.mkdir(DIR, 0750)
                os.chown(DIR, UID, GID)
            except OSError as e:
                print (e)
                error = True
    return error

def _ensurePermissions():
    error = False
    minecraftHome = os.path.dirname(MINECRAFT)
    originalUID = os.geteuid()
    os.seteuid(UID)
    if not os.access(minecraftHome, os.R_OK|os.W_OK):
        print ('Failed to read/write to {PATH}'.format(PATH=minecraftHome))
        error = True
    if not os.access(MINECRAFT, os.R_OK):
        print ('Failed to read {PATH}'.format(PATH=MINECRAFT))
        error = True
    os.seteuid(originalUID)
    return error

def validateConfig():
    errors = []
    errors.append(_ensureIDs())
    if not any(errors):
        errors.append(_ensureDirectory(SOCKET_HOME))
        errors.append(_ensureDirectory(PIDFILE_HOME))
        errors.append(_ensureDirectory(BACKUP_DIR))
        errors.append(_ensurePermissions())
    if any(errors):
        sys.exit(1)