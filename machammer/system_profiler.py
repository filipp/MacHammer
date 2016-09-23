# -*- coding: utf-8 -*-

import json
import shelve
import logging
import os.path
import tempfile
import datetime
import plistlib
import subprocess

from datetime import datetime, timedelta


DEFAULT_DT = 'Hardware'
CACHE_EXPIRE = timedelta(seconds=60*60*1)
PROFILER_PATH = '/usr/sbin/system_profiler'


class SystemProfile(object):
    def __init__(self, dt=DEFAULT_DT):
        types = subprocess.check_output([PROFILER_PATH, '-listDataTypes']).strip()
        self.types = [x[2:].replace('DataType', '') for x in types.split("\n") if x.startswith('SP')]
        self.types.sort()

        if dt not in self.types:
            raise ValueError('Invalid type %s. Should be one of %s' % (dt, ', '.join(self.types)))

        tmp = tempfile.mkstemp()
        self.dt = 'SP%sDataType' % dt

        shelf_path = os.path.join(tempfile.gettempdir(), '%s.system_profiler' % self.dt)
        shelf = shelve.open(shelf_path)

        if shelf.get(dt) and shelf.get('expires'):
            if shelf.get('expires') > datetime.now():
                self._data = shelf[dt]
                return

        try:
            subprocess.call([PROFILER_PATH, self.dt, '-detaillevel', 'full', '-xml'], stdout=tmp[0])
        except Exception as e:
            raise Exception('Failed to fetch system profile: %s' % e)
        
        xml = plistlib.readPlist(tmp[1])
        self._data = xml[0]['_items']
        logging.debug(self._data)

        shelf['expires'] = datetime.now() + CACHE_EXPIRE
        shelf[dt] = self._data
        shelf.close()

    def json(self):
        return json.dumps(self._data)

    def get_keys(self):
        keys = self._data[0].keys()
        keys.sort()
        return keys

    def get_types(self):
        return self.types

    def find(self, k, v):
        """
        Return value(s) of property with key k containing v
        """
        return [x for x in self._data if v in x[k]]

    def __str__(self):
        return str(self._data)

    def __getattr__(self, attr):
        try:
            return self._data[0][attr]
        except KeyError as e:
            raise ValueError('Property "%s" not found' % attr)
        
    def __getitem__(self, attr):
        return self._data[attr]


def types():
    return SystemProfile().get_types()

def keys(dt=DEFAULT_DT):
    return SystemProfile(dt).get_keys()

def get(dt, param):
    return getattr(SystemProfile(dt), param)

def find(dt, k, v):
    return SystemProfile(dt).find(k, v)
