# -*- coding: utf-8 -*-

import os
import plistlib
import subprocess
import sys
import tempfile

from system_profiler import SystemProfile


SERVICEDIR = '/Library/Services'


def ditto(src, dst):
    subprocess.call(['/usr/bin/ditto', src, dst])


def rsync(src, dst, flags='auE'):
    subprocess.call(['rsync', '-' + flags, src, dst])


def dscl(domain='.', *args):
    subprocess.call(['/usr/bin/dscl', domain, ])


def exec_jar(path, user='jkmmadmin'):
    javapath = '/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java'
    if not os.path.exists(javapath):
        raise ValueError('Looks like your machine does not have Java installed')

    subprocess.call(['launchctl', 'asuser', user, javapath, '-jar', path, '-silent'])


def osascript(s):
    subprocess.call(['/usr/bin/osascript', '-e', s])


def tell_app(app, s):
    osascript('tell application "%s" to %s' % (app, s))


def quit_app(app):
    tell_app(app, 'quit')


def copy_app(path):
    """
    Copies path to /Applications folder
    """
    rsync(path.rstrip('/'), '/Applications/')


def add_login_item(path, name=None, hidden=True):
    """
    Adds login item to the current user
    """
    if not name:
        name = os.path.basename(path)

    hidden = 'true' if hidden else 'false'
    tell_app('System Events',
             'make login item at end with properties {path:"%s", hidden:%s, name:"%s"}' % (path, hidden, name))


def remove_login_item(**kwargs):
    """
    Removes login item from the current user
    """
    if not (kwargs.get('name') or kwargs.get('path')):
        raise ValueError('Need either path or name')

    if kwargs.get('name') and kwargs.get('path'):
        raise ValueError('Please specify only path OR name')

    k, v = kwargs.items()[0]
    tell_app('System Events', 'delete every login item whose %s is "%s"' % (k, v))


def create_user(username, realname, password):
    """
    Creates a user
    """
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
    """
    Hides a user
    """
    path = '/Users/%s' % username
    subprocess.call(['dscl', '.', 'create', path, 'IsHidden', '1'])

    if hide_home:
        subprocess.call(['chflags', 'hidden', path])


def delete_user(username, delete_home=True):
    """
    Deletes a user account
    """
    path = '/Users/' + username
    dscl = subprocess.check_output(['dscl', '-plist', '.', 'read', path])
    userinfo = plistlib.readPlistFromString(dscl)

    subprocess.call(['dscl', '.', 'delete', path])

    if delete_home:
        homedir = userinfo['dsAttrTypeStandard:NFSHomeDirectory'][0]
        os.rmdir(homedir)


def make_admin(username):
    subprocess.call(['dscl', '.', '-append', '/Groups/admin', 'users', username])


def is_laptop():
    profile = SystemProfile('SPHardwareDataType')
    return 'Book' in profile.machine_model


def is_desktop():
    return not is_laptop()


def mount_image(path):
    """
    Mounts disk image and returns path to mountpoint
    """
    r = subprocess.check_output(['/usr/bin/hdiutil', 'mount', '-plist', '-nobrowse', path])
    plist = plistlib.readPlistFromString(r)
    for p in [p.get('mount-point') for p in plist.get('system-entities')]:
        if p and os.path.exists(p):
            return p

    raise ValueError('Failed to mount %s' % path)


def mount_and_install(dmg, pkg):
    """
    Mounts the DMG and installs the PKG
    """
    p = mount_image(dmg)
    install_pkg(os.path.join(p, pkg))


def install_profile(path):
    """
    Installs a configuration profile
    """
    subprocess.call(['profiles', '-I', '-F', path])


def install_pkg(pkg, target='/'):
    """
    Installs a package
    """
    subprocess.call(['/usr/sbin/installer', '-pkg', pkg, '-target', target])


def mount_afp(username, password, url, mountpoint=None):
    if mountpoint is None:
        mountpoint = tempfile.mkdtemp()
    subprocess.call(['mount_afp', 'afp://%s:%s@%s' % (username, password, url), mountpoint])
    return mountpoint


def umount(path):
    """
    Unmounts path
    """
    subprocess.call(['umount', path])


def enable_ard(username):
    """
    Enables ARD for username
    """
    subprocess.call(['/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart',
                     '-activate', '-configure',
                     '-access', '-on',
                     '-users', username,
                     '-privs', '-all',
                     '-restart', '-agent'])


def install_su(restart=True):
    """
    Install all Apple software Updates, restart if update requires it
    """
    su_results = subprocess.check_output(['softwareupdate', '-ia'])
    if restart and 'restart' in su_results:
        tell_app('Finder', 'restart')
        sys.exit(0)


def disable_wifi(port='en1'):
    subprocess.call(['networksetup', '-setairportpower', port, 'off'])
    subprocess.call(['networksetup', '-setnetworkserviceenabled', 'Wi-Fi', 'off'])


def log(msg):
    print('*** %s...' % msg)


def install_service(src):
    if not os.path.exists(SERVICEDIR):
        os.mkdir(SERVICEDIR)

    ditto(src, SERVICEDIR)


if __name__ == '__main__':
    delete_user('demouser')
