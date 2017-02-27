# -*- coding: utf-8 -*-

import re
import os
import stat
import inspect

import hooks

APP_SUPPORT_DIR = '/Library/Application Support/'
APP_ID = 'com.github.filipp.machammer'


def get_app_support():
    fp = os.path.join(APP_SUPPORT_DIR, APP_ID)

    if not os.path.exists(fp):
        os.mkdir(fp, mode=07555)

    return fp


def makesource(func):
    """Build runnable source code from function func."""
    # the resulting source code
    r = []
    # skip the decorator and function def
    s = inspect.getsource(func).split('\n')[2:]
    # determine indent level for re-indentation
    indent = re.match(r'^(\s+)', s[0]).group(0)
    r.insert(0, '# -*- coding: utf-8 -*-')
    r.insert(0, '#!/usr/bin/env python')

    for l in s:
        # strip functions indent level
        r.append(l.replace(indent, ''))

    return '\n'.join(r)


def writesource(func, path):
    """Write source of fun to file at path."""
    f = open(path, 'w')
    s = makesource(func)
    f.write(s)
    f.close()


def login(func):
    """Install Python function as a LoginHook."""
    def func_wrapper(hook='login'):
        path = '/var/root/Library/mh_%shook.py' % hook

        writesource(func, path)

        # only root should read and execute
        os.chown(path, 0, 0)
        os.chmod(path, stat.S_IXUSR | stat.S_IRUSR)

        if hook == 'login':
            hooks.login(path)
        else:
            hooks.logout(path)

        return path

    return func_wrapper


def agent(func):
    """Install Python function as a LaunchAgent."""
    def func_wrapper():
        path = os.path.join(get_app_support(), 'launchagent.py')
        writesource(func, path)
        os.chmod(path, stat.S_IXUSR | stat.S_IRUSR)

        return path

    return func_wrapper
