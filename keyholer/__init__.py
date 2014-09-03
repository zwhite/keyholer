#!/usr/bin/env python
"""Listen on a UNIX domain socket to manage user SSH keys.
"""
import atexit
from glob import glob
from os import fdopen, path, remove
from random import randint
from subprocess import Popen, PIPE, STDOUT
from tempfile import mkstemp
from time import time


usercodes = {}
vardir = '/var/tmp'


@atexit.register
def cleanup_on_exit():
    """Removes any temp files we left laying around.
    """
    for file in glob(vardir + '/keyholer.*'):
        remove(file)


def generate_code(username):
    """Generate a user token good for 5 minutes.
    """
    code = '%05d' % randint(10000, 99999)
    usercodes[username] = (code, time())

    return code


def user_keyfile(username):
    """Returns the path to username's authorized_keys file.
    """
    filenames = ['authorized_keys', 'authorized_keys2']
    for filename in filenames:
        keypath = path.expanduser('~%s/.ssh/%s' % (username, filename))
        if path.exists(keypath):
            return keypath

    return None

def validate_key(keytext):
    """Verifies that keytext is a proper entry for authorized_keys
    """
    tmpfd, tmpfile = mkstemp(dir=vardir, prefix='keyholer.')
    cmd = ['ssh-keygen', '-l', '-f', tmpfile]

    # Write the SSH key to a temp file
    with fdopen(tmpfd, 'w') as f:
        f.write(keytext + '\n')

    # Use ssh-keygen to validate the key
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = proc.communicate()
    remove(tmpfile)

    if proc.returncode == 0:
        return True

    print '[ERROR]', stdout
    return False


def verify_code(username, code):
    """Returns True if the code for username is valid
    """
    if username in usercodes and usercodes[username][0] == code:
        if time() - usercodes[username][1] < 300:
            return True

    return false
