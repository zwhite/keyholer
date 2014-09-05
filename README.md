Keyholer - Simple SSH key management for shell servers
======================================================

Keyholer is a web application that will allow your users to add an SSH key
to their authorized_keys file so they can gain access to a system they don't
otherwise have an SSH key for. It attempts to do so in as secure a fashion
as possible.

User Flow/Process:
------------------

    1. User visits keyholer-web
    2. User enters their username, presses submit
        1. keyholer-web submits command, "login <username>"
        2. keyholerd checks for ~<username>/.phonenumber, if bad/missing return False
        3. keyholerd generates and sends random code via SMS, return True
        4. keyholer-web checks return value, returns error if False
    3. keyholer-web displays a verification page, user enters code from SMS
        1. keyholer-web submits command, "verify <username> <code>"
        2. keyholerd checks username and code, returns false if wrong
        3. keyholerd reads the user's authorized_keys, finds list of ID's
        4. keyholerd returns: True\n<list of ID's>
    4. keyholer-web displays the list of existing keys and <input> for a new key
    5. User pastes a new key into the textarea, clicks Submit
        1. keyholer-web submits command, "add_key <username> <code> <ssh_key>"
        2. keyholerd makes sure the code is valid, if not return False
        3. keyholerd makes sure the ssh_key is valid, if not return False
        4. keyholerd adds the key to the user's authorized_keys file

Installation:
-------------

There are two pieces that need to be running; keyholerd and the web frontend.
You can use systemd, runit, screen, or any other daemon management strategy
you'd like. Despite the name keyholerd does not currently support running in
the background as a daemon.

To run the web component you can use your favorite WSGI stack. My personal 
setup uses nginx to proxy the requests back to a gunicorn app server.

Configuration
-------------

Keyholer requires a configuration file. You can find a sample config in
etc/keyholer.conf.example. You should install your configuration as 
/etc/keyholer.conf and it must be valid JSON.

  admin_user
    The username of the server's owner. This user will get SMS's anytime a
    user's password is reset

  web_user
    The username the web app will run as

  group
    The group for the web_user

  socket
    The path for the socket the frontend uses to communicate with the backend.
    This directory must be owned by **web_user**:**group** and be mode 700. If
    if does not exist it will be created by keyholerd.

  sms_phone_number
    The phone number that codes will be sent from

  token_ttl
    How many seconds a token is good for. Defaults to 300 (5 minutes)

  twilio_sid
    The account sid for your twilio account

  twilio_auth_token
    The AuthToken for your twilio account

Twilio
------

Sign up for an account, register a phone number, and get your auth_token and
sid at their website:

    http://twilio.com

This is required to send the code via SMS.

systemd
-------

If you are on a system which uses systemd as the init system, you will find
files that can be used to start keyholer at boot time in etc/systemd.
