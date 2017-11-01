# -*- coding: utf-8 -*-

import os
import sys
import logging
import plistlib
import tempfile
import subprocess

from .system_profiler import SystemProfile


SERVICEDIR = '/Library/Services'


def get_plist(path):
    """Return plist dict regardless of format.

    """
    plist = subprocess.check_output(['/usr/bin/plutil',
                                     '-convert', 'xml1',
                                     path, '-o', '-'])
    return plistlib.readPlistFromString(plist)


def call(*args):
    """Shortcut for subprocess.call.

    > call('ls', '/Users')
    """
    args = [str(x) for x in args]
    subprocess.call(args)


def popen(cmd, input=None):
    """Shortcut for Popen/communicate()."""
    proc = subprocess.Popen(cmd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (res, err) = proc.communicate(input)

    if err:
        raise Exception(err)

    return res


def check_output(*args):
    """Shortcut for subprocess.check_output."""
    args = [str(x) for x in args]
    result = subprocess.check_output(args).strip()

    if len(result) < 1:
        result = None

    return result


def rmdir(path):
    """Shortcut for deleting a directory."""
    call('/bin/rm', '-r', path)


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
    call('/usr/bin/ditto', src, dst)


def rsync(src, dst, flags='auE'):
    """Shortcut for rsync."""
    call('/usr/bin/rsync', '-' + flags, src, dst)


def dscl(domain='.', *args):
    """Shortcut for dscl."""
    subprocess.call(['/usr/bin/dscl', domain] + args)


def exec_jar(path, user):
    javapath = '/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java'
    if not os.path.exists(javapath):
        raise Exception('Looks like your machine does not have Java installed')

    call('/bin/launchctl', 'asuser', user, javapath, '-jar', path, '-silent')


def osascript(s):
    try:
        return check_output('/usr/bin/osascript', '-e', s)
    except Exception as e:
        raise Exception('The AppleScript returned an error: %s' % e)


def tell_app(app, s):
    return osascript('tell application "%s" to %s' % (app, s))


def quit_app(app):
    tell_app(app, 'quit')


def copy_app(path):
    """Copy path to /Applications folder."""
    rsync(path.rstrip('/'), '/Applications/')


def unzip_app(path):
    """Install zipped application."""
    call('/usr/bin/unzip', '-q', path, '-d', '/Applications')


def enable_ard(username, privs='-all'):
    """Enable Apple Remote Desktop for username."""
    subprocess.call(['/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart',
                     '-activate', '-configure',
                     '-access', '-on',
                     '-users', username,
                     '-privs', privs,
                     '-restart', '-agent'])


def sleep():
    """Put this Mac to sleep."""
    tell_app('Finder', 'sleep')


def is_laptop():
    profile = SystemProfile('Hardware')
    return 'Book' in profile.machine_model


def is_desktop():
    return not is_laptop()


def mount_image(path, mp=None):
    """Mount disk image and return path to mountpoint."""
    logging.debug('Mounting DMG %s' % path)
    mp = mp or tempfile.mkdtemp()
    p = subprocess.Popen(['/usr/bin/hdiutil', 'mount',
                         '-mountpoint', mp, 
                         '-nobrowse', path],
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    # work around EULA prompt
    out, err = p.communicate(input=b'Q\nY\n')
    logging.debug('mount_image got %s' % out)

    if err:
        raise Exception(err)

    return mp


def mount_and_install(dmg, pkg):
    """Mounts the DMG and installs the PKG."""
    p = mount_image(dmg)
    install_pkg(os.path.join(p, pkg))


def install_profile(path):
    """Install a configuration profile."""
    subprocess.call(['/usr/bin/profiles', '-I', '-F', path])


def install_pkg(pkg, target='/'):
    """Install a package."""
    call('/usr/sbin/installer', '-pkg', pkg, '-target', target)


def mount_url(url):
    """Mount disk image from URL.
    Return path to mounted volume."""
    if url.startswith('http'):
        p = curl(url)
        return mount_image(p)
    
    raise Exception('URL scheme not supported')


def mount_afp(url, username, password, mountpoint=None):
    """Mount AFP share."""
    if mountpoint is None:
        mountpoint = tempfile.mkdtemp()
    url = 'afp://%s:%s@%s' % (username, password, url)
    call('/sbin/mount_afp', url, mountpoint)
    return mountpoint


def umount(path):
    """Unmount path."""
    call('/sbin/umount', path)


def install_su(restart=True):
    """Install all available Apple software Updates,
    restart if any update requires it."""
    su_results = subprocess.check_output(['/usr/sbin/softwareupdate', '-ia'])
    if restart and ('restart' in su_results):
        # Easy way to reboot without special privileges
        tell_app('Finder', 'restart')
        sys.exit(0)


def install_service(src):
    """Copy .service to systemwide Services folder."""
    if not os.path.exists(SERVICEDIR):
        os.mkdir(SERVICEDIR)

    ditto(src, SERVICEDIR)


def clear_xattr(path):
    """Clear all extended attributes on path."""
    call('/usr/bin/xattr', '-c', path)


def create_os_media(src, dst):
    fp = os.path.join(src, 'Contents/Resources/createinstallmedia')
    call(fp, '--volume', dst, '--applicationpath', src, '--nointeraction')


def curl(url, *args):
    """Fetch URL with curl and return path to download."""
    args = list(args)
    if '-o' not in args:
        dst = tempfile.NamedTemporaryFile(delete=False)
        of = dst.name
        args = args + ['-o', of]
    else:
        i = args.index('-o')
        of = args[i+1]
    
    if '-v' not in args:
        args.append('--silent')
    
    args.append(url)
    call('/usr/bin/curl', *args)
    
    return of


def log(msg):
    logging.debug(msg)
