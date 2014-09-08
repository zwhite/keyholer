#!/usr/bin/env python
"""Library for Keyholer.
"""
import json
from os import path


__version__ = '0.7.0'

# Attempt to load a configuration from the config file
conf = None

for file in ('keyholer.conf', 'etc/keyholer.conf', '/etc/keyholer.conf'):
    if path.exists(file):
        print '[INFO] Loading config file from %s.' % file

        try:
            conf = json.load(open(file))
            break

        except ValueError, e:
            print '[ERROR] Could not parse %s: %s' % (file, e)
            exit(1)

if not conf:
    print '[ERROR] No config file could be found! Please setup one of:\n'
    print ' * /etc/keyholer.conf'
    print ' * etc/keyholer.conf'
    print ' * keyholer.conf'
    exit(1)
