#!/usr/bin/env python
from socket import socket, AF_UNIX, SOCK_STREAM
import sys

from keyholer import conf


class KeyholerException(Exception):
    pass


class KeyholerClient(object):
    """
        Class for interacting with the keyholer backend.
    """
    def __init__(self, sock=conf['socket']):
        self.s = None
        self.socket = sock

    def _readline(self):
        """Iterate over the data in a socket's receive buffer line by line
        """
        buffer = self.s.recv(4096)

        while True:
            if '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                yield line

            else:
                more = self.s.recv(4096)

                if not more:
                    break

                buffer = buffer+more

        if buffer:
            yield buffer

    def command(self, command):
        """Send a command to the backend and return the response
        """
        self.s = socket(AF_UNIX, SOCK_STREAM)
        self.s.connect(self.socket)
        self.s.sendall(command + "\n")

        result = '\n'.join([line for line in self._readline()])
        self.s.close()

        if result == 'Exception':
            raise KeyholerException

        return result

    # Commands the user can use to interact with KeyholerD
    def login(self, user):
        """Sends a code to the phone number on file for user.
        """
        return self.command('login %s' % user)

    def verify(self, user, code):
        """Verifies that a user's code is correct

        Returns a list of SSH keys that are already available for the user,
        or False.
        """
        return self.command('verify %s %s' % (user, code))

    def add_key(self, user, code, ssh_keytext):
        """Adds a key to the user's authorized_keys file.
        """
        return self.command('add_key %s %s %s' % (user, code, ssh_keytext))
