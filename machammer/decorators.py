# -*- coding: utf-8 -*-

import re
import os
import stat
import inspect

import hooks


def login(func):
    def func_wrapper(hook='login'):
        path = '/var/root/Library/mh_%shook.py' % hook

        # skip the decorator and function def
        s = inspect.getsource(func).split('\n')[2:]

        # determine indent level for re-indentation
        indent = re.match(r'^(\s+)', s[0]).group(0)
        f = open(path, 'w')
        f.write('#!/usr/bin/env python\n')

        for l in s:
            f.write(l.replace(indent, '') + '\n')

        f.close()
        # only root should read and execute
        os.chown(path, 0, 0)
        os.chmod(path, stat.S_IXUSR | stat.S_IRUSR)

        if hook == 'login':
            hooks.login(path)
        else:
            hooks.logout(path)

        return path

    return func_wrapper
