from keyholer import generate_code, user_keyfile, validate_key, verify_code
from keyholer.line_request_handler import LineRequestHandler


class KeyholerDaemon(LineRequestHandler):
    """
        The class that actually implements the Keyholer backend
    """
    def cmd_login(self, username):
        """Generate a token for a user and send it to them via SMS.
        """
        authorized_keys = user_keyfile(username)

        if authorized_keys:
            code = generate_code(username)
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
        keys = validate_key(open(authorized_keys).read())  # FIXME: remove this open() call
        return 'True\n' + keys

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
