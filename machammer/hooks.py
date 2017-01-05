# -*- coding: utf-8 -*-

import defaults

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
    defaults.set('/Library/LaunchAgents/%s' % label, 'Label', label)
    defaults.set('/Library/LaunchAgents/%s' % label, 'Program', path)
    defaults.set('/Library/LaunchAgents/%s' % label, 'StartOnMount',
                 '-boolean',
                 'TRUE')
    defaults.set('/Library/LaunchAgents/%s' % label, 'WatchPaths', '-array',
                 mountpoint)
