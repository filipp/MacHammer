# -*- coding: utf-8 -*-
"""machammer.users."""

import re
import os
import logging
import plistlib
import subprocess

from .functions import tell_app, check_output, call


def dscl(*args):
    """Shortcut for accessing the local DS."""
    return check_output('/usr/bin/dscl', '.', *args)


def get_info(username):
    path = '/Users/' + username
    s = check_output('/usr/bin/dscl', '-plist', '.', 'read', path)
    return plistlib.readPlistFromString(s)


def nextid(node='/Users', attr='UniqueID'):
    """Return next available ID for DS node/attribute."""
    s = dscl('-list', node, attr)
    ids = re.split(r'\s+', s)[1::2]
    return max([int(x) for x in ids]) + 1


def add_login_item(path, name=None, hidden=True):
    """Add login item to the current user."""
    if not name:
        name = os.path.basename(path)

    hidden = 'true' if hidden else 'false'
    cmd = 'make login item at end with properties {path:"%s", hidden:%s, name:"%s"}'
    tell_app('System Events', cmd % (path, hidden, name))


def remove_login_item(**kwargs):
    """Remove login item from the current user."""
    if not (kwargs.get('name') or kwargs.get('path')):
        raise ValueError('Need either path or name')

    if kwargs.get('name') and kwargs.get('path'):
        raise ValueError('Please specify only path OR name')

    k, v = kwargs.items()[0]
    tell_app('System Events', 'delete every login item whose %s is "%s"' % (k, v))


def create_user(realname, password, username=None, uid=None, gid=20):
    """Create a user account."""
    if uid is None:
        uid = nextid()

    if gid is None:
        gid = nextid('/Groups', 'PrimaryGroupID')

    if username is None:
        username = realname.lower().replace(' ', '.')

    path = '/Users/' + username
    dscl('create', path)
    dscl('create', path, 'RealName', realname)
    dscl('create', path, 'UniqueID', uid)
    dscl('create', path, 'PrimaryGroupID', gid)
    dscl('create', path, 'UserShell', '/bin/bash')
    dscl('create', path, 'NFSHomeDirectory', path)

    dscl('passwd', path, password)

    template = '/System/Library/User Template/'
    call('/usr/bin/ditto', template + 'English.lproj/', path)
    call('/usr/bin/ditto', template + 'Non_localized/', path)
    call('/usr/sbin/chown', '-R', username + ':staff', path)

    return get_info(username)


def hide_user(username, hide_home=True):
    """Hide a user account."""
    path = '/Users/%s' % username
    dscl('create', path, 'IsHidden', '1')

    if hide_home:
        subprocess.call(['/usr/bin/chflags', 'hidden', path])


def delete_user(username, delete_home=True):
    """Delete a user account."""
    path = '/Users/' + username
    userinfo = get_info(username)

    dscl('delete', path)

    if delete_home:
        homedir = userinfo['dsAttrTypeStandard:NFSHomeDirectory'][0]
        logging.debug('Deleting home directory: %s' % homedir)
        call('/bin/rm', '-r', homedir)


def make_admin(username):
    """Give admin rights to username."""
    dscl('-append', '/Groups/admin', 'users', username)
