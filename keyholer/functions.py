#!/usr/bin/env python
"""Listen on a UNIX domain socket to manage user SSH keys.
"""
import re
from os import fdopen, path, remove
from random import randint
from subprocess import Popen, PIPE, STDOUT
from tempfile import mkstemp
from time import time

from twilio.rest import TwilioRestClient

from keyholer import conf


# Setup some unfortunately necessary globalish vars
twilio = TwilioRestClient(conf['twilio_sid'], conf['twilio_auth_token'])
usercodes = {}


def generate_code(username):
    """Generate a user token good for 5 minutes.
    """
    code = '%05d' % randint(10000, 99999)
    usercodes[username] = (code, time())

    return code


def send_sms(username, message):
    """Sends an SMS to a user using twilio.
    """
    phonenumber = user_phonenumber(username)

    if not phonenumber:
        print '[ERROR] No phone number for %s!' % username
        return False

    print '[INFO] Sending SMS to %s(%s): %s' % (username, phonenumber, message)
    twilio.sms.messages.create(to=phonenumber, body=message,
                               from_=conf['sms_phone_number'])
    return True


def user_keyfile(username):
    """Returns the path to username's authorized_keys file.
    """
    filenames = ['authorized_keys', 'authorized_keys2']

    for filename in filenames:
        keypath = path.expanduser('~%s/.ssh/%s' % (username, filename))

        if path.exists(keypath):
            return keypath

    print '[ERROR] No authorized_keys file for %s!' % username
    return None


def user_phonenumber(username):
    """Look up a user's phone number.
    """
    phonenumber = path.expanduser('~%s/.phonenumber' % username)

    if not path.exists(phonenumber):
        print '[ERROR] %s does not have a .phonenumber file!' % username
        return None

    phonenumber = open(phonenumber).read().strip()

    # My users might do weird things since they are US centric. Try to
    # massage their phone number into E164 format so twilio will accept it
    phonenumber = re.sub('[^0-9+]', '', phonenumber)

    if phonenumber[0] != '+':
        if len(phonenumber) == 11 and phonenumber[1] == 1:
            # Looks like a US number without the +
            phonenumber = '+' + phonenumber

        elif len(phonenumber) == 10:
            # Looks like a US number without the +1
            phonenumber = '+1' + phonenumber

        elif phonenumber[:3] == '011':
            # Looks like an international number as dialed from the US
            phonenumber = '+' + phonenumber[3:]

        else:
            # Oh boy, I'm not sure what they've done, just slap a + on it
            phonenumber = '+' + phonenumber

    return phonenumber


def validate_key(keytext):
    """Verifies that keytext is a proper entry for authorized_keys
    """
    tmpfd, tmpfile = mkstemp(prefix='keyholer.')
    cmd = ['ssh-keygen', '-l', '-f', tmpfile]

    # Write the SSH key to a temp file
    with fdopen(tmpfd, 'w') as f:
        f.write(keytext + '\n')

    # Use ssh-keygen to validate the key
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = proc.communicate()
    remove(tmpfile)

    if proc.returncode == 0:
        return stdout

    print '[ERROR]', stdout
    return False


def verify_code(username, code):
    """Returns True if the code for username is valid
    """
    if username in usercodes and usercodes[username][0] == code:
        if time() - usercodes[username][1] < conf['token_ttl']:
            return True

    return False
