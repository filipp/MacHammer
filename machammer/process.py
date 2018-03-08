# -*- coding: utf-8 -*-

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
        self._prefs = defaults.as_dict(domain)
        
    def __getattr__(self, k):
        try:
            return self._prefs[k]
        except AttributeError:
            return super(Prefs, self).getattr(k)
    
    def __setattr__(self, k, v):
        print('Setting attribute: %s' % k)
        self._prefs[k] = v


class App(object):
    def __init__(self, domain):
        self.domain = domain
        self.prefs = Prefs(domain)

    def launch(self):
        pass
    
    def quit(self):
        pass
    
    def is_installed(self):
        return False
    
    def version(self):
        return False

