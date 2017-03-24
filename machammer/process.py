# -*- coding: utf-8 -*-

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
