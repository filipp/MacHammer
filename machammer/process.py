# -*- coding: utf-8 -*-

try:
    import CoreFoundation
    from AppKit import NSWorkspace, NSUserDefaults, NSRunningApplication
except ImportError:
    raise Exception('Sorry, but it looks like your Python installation lacks PyObjc support')

from . import defaults
from .functions import call, tell_app


def pidof(name):
    pass


def is_running(name):
    s = 'name of every application process contains "%s"' % name
    a = tell_app('System Events', s)
    return a == 'true'


def is_active(name):
    """Return True if process with name is frontmost
    """
    s = 'name of first application process whose frontmost is true'
    a = tell_app('System Events', s)
    return a == name


def activate(name):
    tell_app(name, 'activate')


def quit(name):
    pass


def kill(name, signal='TERM'):
    call('/usr/bin/killall', '-' + signal, name)


def open(name):
    call('/usr/bin/open', '-a', name)


class Prefs(object):

    def __init__(self, domain):
        self.domain = domain
        args = [self.domain, CoreFoundation.kCFPreferencesCurrentUser, CoreFoundation.kCFPreferencesAnyHost]
        self.keys = CoreFoundation.CFPreferencesCopyKeyList(*args)
        self.prefs = CoreFoundation.CFPreferencesCopyMultiple(self.keys, *args)

        if not self.prefs:
            raise ValueError('Invalid domain: %s' % self.domain)

    def get(self, key):
        if key not in self.keys:
            raise Exception('Invalid key: %s' % key)

        return self.prefs.get(key)

    def set(self, key, value):
        CoreFoundation.CFPreferencesSetAppValue(key, value, self.domain)


class App(object):

    ws = NSWorkspace.sharedWorkspace()
    
    def __init__(self, domain=None, name=None):
        if not (domain or name):
            raise Exception('Name or domain must be provided')

        self.domain = domain
        self.prefs = Prefs(self.domain)
        self.apps = NSRunningApplication.runningApplicationsWithBundleIdentifier_(self.domain)

        if self.apps:
            self.app = self.apps[0]
            name = name or self.app.localizedName()

        self.name = name

    def is_running(self):
        running = self.ws.runningApplications()
        return self.domain in [a.bundleIdentifier() for a in running]

    def tell(self):
        raise NotImplementedError('Scripting support not implemented')

    def activate(self):
        raise NotImplementedError()

    def launch(self):
        return self.ws.launchApplication_(self.name)
    
    def is_active(self):
        return self.app.isActive()

    def quit(self):
        return self.app.terminate()
    
    def is_installed(self):
        raise NotImplementedError()
    
    def version(self):
        raise NotImplementedError()

