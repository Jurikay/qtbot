# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

import os
import urllib.request


def get_env_values():
    """Gather system information."""
    user = os.getlogin()
    platform = os.name
    if platform == "nt":
        computer = os.environ['COMPUTERNAME']  # Does not work on mac os
    else:   
        computer = os.uname()[1]
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

    print(user, computer, external_ip)
    return user + "@" + computer + ":" + external_ip