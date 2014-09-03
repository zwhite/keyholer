Keyholer - Simple SSH key management for shell servers
======================================================

This program is currently a work in progress- you may find it useful as is
but it is not considered feature complete yet.

Keyholer is a web application that will allow your users to add an SSH key
to their authorized_keys file so they can gain access to a system they don't
otherwise have an SSH key for. It attempts to do so in as secure a fashion
as possible.

Process:

    1. User visits https://darkstar.frop.org/
    2. User enters their username, presses submit
        1. keyholer-fe submits command, "login <username>"
        2. keyholer-be checks for ~<username>/.phonenumber, if bad/missing return False
        3. keyholer-be generates and sends random code via SMS, return True
        4. keyholer-fe checks return value, returns error if False
    3. keyholer-fe displays a verification page, user enters code from SMS
        1. keyholer-fe submits command, "verify <username> <code>"
        2. keyholer-be checks username and code, returns false if wrong
        3. keyholer-be reads the user's authorized_keys, finds list of ID's
        4. keyholer-be returns: True <comma-separated list of ID's>
    4. keyholer-fe displays the list of existing keys and a textarea for a new key
    5. User pastes a new key into the textarea, clicks Submit
        1. keyholer-fe submits command, "add_key <username> <code> <ssh_key>"
        2. keyholer-be makes sure the code is valid, if not return False
        3. keyholer-be makes sure the ssh_key is valid, if not return False
        4. keyholer-be adds the key to the user's authorized_keys file
