# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import os
import urllib.request


def get_env_values():
    """Gather system information."""
    user = os.getlogin()
    computer = os.environ['COMPUTERNAME']
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

    print(user, computer, external_ip)
    return user + "@" + computer + " from " + external_ip