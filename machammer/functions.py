# -*- coding: utf-8 -*-

import os
import plistlib
import subprocess
import sys
import tempfile

from xml.parsers.expat import ExpatError
from system_profiler import SystemProfile


SERVICEDIR = '/Library/Services'


def call(*args):
    """Shorthand for subprocess.call.

    > call('ls', '/Users')
    """
    subprocess.call(args)


def rmdir(path):
    """Shortcut for deleting a directory."""
    call('rm', '-r', path)


def display_notification(msg, title='', subtitle=''):
    """Display notification with optional title and subtitle.

    display_notification('Mymessage')
    """
    msg = msg.replace('"', '\\"')
    title = title.replace('"', '\\"')
    subtitle = subtitle.replace('"', '\\"')
    cmd = 'display notification "{0}" with title "{1}" subtitle "{2}"'
    osascript(cmd.format(msg, title, subtitle))


def ditto(src, dst):
    """Shortcut for ditto."""
    subprocess.call(['/usr/bin/ditto', src, dst])


def rsync(src, dst, flags='auE'):
    """Shortcut for rsync."""
    subprocess.call(['/usr/bin/rsync', '-' + flags, src, dst])


def dscl(domain='.', *args):
    """Shortcut for dscl."""
    subprocess.call(['/usr/bin/dscl', domain] + args)


def exec_jar(path, user):
    javapath = '/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java'
    if not os.path.exists(javapath):
        raise ValueError('Looks like your machine does not have Java installed')

    subprocess.call(['/bin/launchctl', 'asuser', user, javapath, '-jar', path, '-silent'])


def osascript(s):
    subprocess.call(['/usr/bin/osascript', '-e', s])


def tell_app(app, s):
    osascript('tell application "%s" to %s' % (app, s))


def quit_app(app):
    tell_app(app, 'quit')


def copy_app(path):
    """Copy path to /Applications folder."""
    rsync(path.rstrip('/'), '/Applications/')


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


def enable_ard(username):
    """Enable Apple Remote Desktop for username."""
    subprocess.call(['/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart',
                     '-activate', '-configure',
                     '-access', '-on',
                     '-users', username,
                     '-privs', '-all',
                     '-restart', '-agent'])


def is_laptop():
    profile = SystemProfile('Hardware')
    return 'Book' in profile.machine_model


def is_desktop():
    return not is_laptop()


def mount_image(dmg):
    """Mount disk image and return path to mountpoint."""
    p = subprocess.Popen(['/usr/bin/hdiutil', 'mount', '-plist', '-nobrowse', dmg],
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    r, e = p.communicate(input=b'Q\nY\n')

    if e:
        raise Exception(e)

    try:
        plist = plistlib.readPlistFromString(r)
    except ExpatError:  # probably a EULA-image, return None instead of breaking
        return None

    for p in [p.get('mount-point') for p in plist.get('system-entities')]:
        if p and os.path.exists(p):
            return p

    raise Exception('Failed to mount %s' % dmg)


def mount_and_install(dmg, pkg):
    """Mountsthe DMG and installs the PKG."""
    p = mount_image(dmg)
    install_pkg(os.path.join(p, pkg))


def install_profile(path):
    """Install a configuration profile."""
    subprocess.call(['/usr/bin/profiles', '-I', '-F', path])


def install_pkg(pkg, target='/'):
    """Install a package."""
    subprocess.call(['/usr/sbin/installer', '-pkg', pkg, '-target', target])


def mount_afp(url, username, password, mountpoint=None):
    """Mount AFP share."""
    if mountpoint is None:
        mountpoint = tempfile.mkdtemp()
    subprocess.call(['/sbin/mount_afp', 'afp://%s:%s@%s' % (username, password, url), mountpoint])
    return mountpoint


def umount(path):
    """Unmount path."""
    subprocess.call(['/sbin/umount', path])


def install_su(restart=True):
    """Install all available Apple software Updates, restart if update requires it."""
    su_results = subprocess.check_output(['/usr/sbin/softwareupdate', '-ia'])
    if restart and ('restart' in su_results):
        tell_app('Finder', 'restart')
        sys.exit(0)


def disable_wifi(port='en1'):
    subprocess.call(['/usr/sbin/networksetup', '-setairportpower', port, 'off'])
    subprocess.call(['/usr/sbin/networksetup', '-setnetworkserviceenabled', 'Wi-Fi', 'off'])


def log(msg):
    print('*** %s...' % msg)


def install_service(src):
    """Copy .service to systemwide Services folder."""
    if not os.path.exists(SERVICEDIR):
        os.mkdir(SERVICEDIR)

    ditto(src, SERVICEDIR)
