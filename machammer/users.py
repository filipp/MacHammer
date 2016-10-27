# -*- coding: utf-8 -*-
"""machammer.users."""

import os
import plistlib
import subprocess

from .functions import tell_app


def add_login_item(path, name=None, hidden=True):
    """Add login item to the current user."""
    if not name:
        name = os.path.basename(path)

    hidden = 'true' if hidden else 'false'
    tell_app('System Events',
             'make login item at end with properties {path:"%s", hidden:%s, name:"%s"}' % (path, hidden, name))


def remove_login_item(**kwargs):
    """Remove login item from the current user."""
    if not (kwargs.get('name') or kwargs.get('path')):
        raise ValueError('Need either path or name')

    if kwargs.get('name') and kwargs.get('path'):
        raise ValueError('Please specify only path OR name')

    k, v = kwargs.items()[0]
    tell_app('System Events', 'delete every login item whose %s is "%s"' % (k, v))


def create_user(username, realname, password):
    """Create a user account."""
    os.system("""dscl . create /Users/{0}
                 dscl . create /Users/{0} RealName "{1}"
                 dscl . passwd /Users/{0} {2}
                 dscl . create /Users/{0} UniqueID 501
                 dscl . create /Users/{0} PrimaryGroupID 80
                 dscl . create /Users/{0} UserShell /bin/bash
                 dscl . create /Users/{0} NFSHomeDirectory /Users/{0}
                 cp -R /System/Library/User\ Template/English.lproj /Users/{0}
                 chown -R {0}:staff /Users/{0}""".format(username, realname, password))


def hide_user(username, hide_home=True):
    """Hide a user account."""
    path = '/Users/%s' % username
    subprocess.call(['dscl', '.', 'create', path, 'IsHidden', '1'])

    if hide_home:
        subprocess.call(['/usr/bin/chflags', 'hidden', path])


def delete_user(username, delete_home=True):
    """Delete a user account."""
    path = '/Users/' + username
    dscl = subprocess.check_output(['dscl', '-plist', '.', 'read', path])
    userinfo = plistlib.readPlistFromString(dscl)

    subprocess.call(['dscl', '.', 'delete', path])

    if delete_home:
        homedir = userinfo['dsAttrTypeStandard:NFSHomeDirectory'][0]
        os.rmdir(homedir)


def make_admin(username):
    """Give admin rights to username."""
    subprocess.call(['dscl', '.', '-append', '/Groups/admin', 'users', username])
