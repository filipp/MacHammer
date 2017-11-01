# -*- coding: utf-8 -*-

from . import defaults

PREF_DOMAIN = 'com.apple.loginwindow'


def login(path=None):
    """Set login hook to path, or disable login hook."""
    if path is None:
        return defaults.delete(PREF_DOMAIN, 'LoginHook')

    return defaults.set(PREF_DOMAIN, 'LoginHook', path)


def logout(path=None):
    """Set logout hook to path, or disable logout hook."""
    if path is None:
        return defaults.delete(PREF_DOMAIN, 'LogoutHook')

    return defaults.set(PREF_DOMAIN, 'LogoutHook', path)


def reboot(path=None):
    """Set reboot hook to path, or disable reboot hook."""
    pass


def shutdown(path=None):
    """Set shutdown hook to path, or disable shutdown hook."""
    pass


def mount(mountpoint, path=None):
    """Execute path if mountpoint is mounted. Set path to None to disable."""
    label = 'com.github.filipp.machammer.mounthook'
    plist = '/Library/LaunchDaemons/' + label
    defaults.set(plist, 'Label', label)
    defaults.set(plist, 'Program', path)
    defaults.set(plist, 'StartOnMount', '-boolean', 'TRUE')
    defaults.set(plist, 'WatchPaths', '-array', mountpoint)


def agent(path=None):
    """Execute path if mountpoint is mounted. Set path to None to disable."""
    label = 'com.github.filipp.machammer.loginhook'
    plist = '/Library/LaunchAgents/' + label
    defaults.set(plist, 'Label', label)
    defaults.set(plist, 'Program', path)
    defaults.set(plist, 'RunAtLoad', '-boolean', 'TRUE')
