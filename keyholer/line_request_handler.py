#!/usr/bin/env python
"""Listen on a UNIX domain socket to manage user SSH keys.

Process:

    1. User visits https://darkstar.frop.org/
    2. User enters their username, presses submit
        2a. keyholer-fe submits command over socket, "login <username>"
        2b. keyholer-be checks for ~<username>/.phonenumber, if bad/missing 
            return False
        2c. keyholer-be generates and sends random code via SMS, return True
        2d. keyholer-fe checks return value, returns error if False
    3. keyholer-fe displays a verification page, user enters code from SMS
        3a. keyholer-fe submits command over socket, "verify <username> <code>"
        3b. keyholer-be checks username and code, returns false if wrong
        3c. keyholer-be reads the user's authorized_keys, finds list of ID's
        3d. keyholer-be returns: True <comma-separated list of ID's>
    4. keyholer-fe displays the list of existing keys, textarea for new key
    5. User pastes a new key into the textarea, clicks Submit
        5a. keyholer-fe submits command over socket, 
            "add_key <username> <code> <ssh_key>"
        5b. keyholer-be makes sure the code is valid, if not return False
        5b. keyholer-be makes sure the ssh_key is valid, if not return False
        5c. keyholer-be adds the key to the user's authorized_keys file
"""
import atexit
from SocketServer import StreamRequestHandler, UnixStreamServer
from glob import glob
from os import fdopen, path, remove
from random import randint
from subprocess import Popen, PIPE, STDOUT
from tempfile import mkstemp
from time import time
from traceback import print_exc


vardir = '/var/tmp'


class LineRequestHandler(StreamRequestHandler):
    """A server that reads a line and processes it as a single command.

    If the first word of the line matches a cmd_<name> function, that function
    will be called with the remaining words passed in as positional arguments.

    If the first word does not have a corresponding cmd_<name> function we
    return "None".

    Any uncaught exception will result in "Exception" being returned to the 
    client.
    """
    def handle(self):
        cmd = self.rfile.readline().strip().split()
        print "client wrote:", cmd

        if hasattr(self, 'cmd_' + cmd[0]):
            try:
                result = getattr(self, 'cmd_' + cmd[0])(*cmd[1:])
                self.write(result)

            except Exception, e:
                print_exc()
                self.write('Exception')

        else:
            self.write('None')

    def write(self, data):
        return self.wfile.write(data)


class KeyholerBE(LineRequestHandler):
    """
        The class that actually implements the Keyholer backend
    """
    def cmd_login(self, username):
        """Generate a token for a user and send it to them via SMS.
        """
        authorized_keys = user_keyfile(username)

        if authorized_keys:
            code = '%05d' % randint(10000, 99999)
            usercodes[username] = (code, time())
            # FIXME: Send the code via sms
            print 'Code for %s: %s' % (username, code)
            return 'True'

        return 'False'

    def cmd_verify(self, username, code):
        """Verify the user's code and return a list of existing keys.
        """
        if not verify_code(username, code):
            return False

        authorized_keys = user_keyfile(username)

        if not authorized_keys:
            return 'False'

        # If they made it this far return a list of keys
        keys = []

        with open(authorized_keys) as f:
            for line in f.readlines():
                cipher, keytext, comment = line.split(' ', 2)
                keys.append(comment)

        return 'True %s' % ','.join(keys)


    def cmd_add_key(self, username, code, *ssh_key):
        """Add the provided ssh_key to username's authorized_keys file.
        """
        ssh_key = ' '.join(ssh_key)

        if not verify_code(username, code):
            print '[ERROR] Invalid code for %s' % username
            return 'False'

        if not validate_key(ssh_key):
            print '[ERROR] Invalid key for %s' % username
            return 'False'

        authorized_keys = user_keyfile(username)
        # If they've got this far add the new key
        with open(authorized_keys, 'a') as f:
            f.write(ssh_key + '\n')

        return 'True'


@atexit.register
def cleanup_on_exit():
    """Removes any temp files we left laying around.
    """
    for file in glob(vardir + '/keyholer.*'):
        remove(file)


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


if __name__ == "__main__":
    # Create the server, listening on a unix domain socket
    usercodes = {}
    server = UnixStreamServer(vardir + '/keyholer.socket', KeyholerBE)
    server.serve_forever()
