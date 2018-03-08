# -*- coding: utf-8 -*-

import plistlib
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


def domains(*args):
    s = check_output(DEFAULTS_PATH, 'domains').decode()
    return [i.strip() for i in s.split(',')]


def as_dict(domain):
    s = check_output(DEFAULTS_PATH, 'export', domain, '-')
    return plistlib.loads(s)
