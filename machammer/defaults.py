# -*- coding: utf-8 -*-

from .functions import call, check_output

DEFAULTS_PATH = '/usr/bin/defaults'


def defaults(*args):
    if any(i == 'read' for i in args):
        return check_output(DEFAULTS_PATH, *args)

    return call(DEFAULTS_PATH, *args)


def get(*args):
    return defaults('read', *args)


def set(*args):
    return defaults('write', *args)


def delete(*args):
    return defaults('delete', *args)
