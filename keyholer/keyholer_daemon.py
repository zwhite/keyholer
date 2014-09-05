from keyholer import conf
from keyholer.functions import generate_code, send_sms, user_keyfile
from keyholer.functions import validate_key, verify_code
from keyholer.line_request_handler import LineRequestHandler


class KeyholerDaemon(LineRequestHandler):
    """
        The class that actually implements the Keyholer backend
    """
    def cmd_login(self, username):
        """Generate a token for a user and send it to them via SMS.
        """
        if not user_keyfile(username):
            return 'False'

        code = generate_code(username)

        if not send_sms(username, code):
            print '[ERROR] Could not send SMS to %s!' % username
            return 'False'

        return 'True'

    def cmd_verify(self, username, code):
        """Verify the user's code and return a list of existing keys.
        """
        if not verify_code(username, code):
            return False

        authorized_keys = user_keyfile(username)

        if not authorized_keys:
            return 'False'

        # If they made it this far return a list of keys
        # FIXME: remove this open() call
        keys = validate_key(open(authorized_keys).read())
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

        # Tell the admin what we've done
        if conf['admin_user']:
            send_sms(conf['admin_user'], '%s has added a new key.' % username)

        return 'True'
