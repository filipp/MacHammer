# -*- coding: utf-8 -*-
"""Network-related machammer functions."""

import re
from .process import kill
from .functions import call, check_output
from .system_profiler import SystemProfile


def networksetup(*args):
    return check_output('/usr/sbin/networksetup', *args)


def systemsetup(*args):
    return check_output('/usr/sbin/systemsetup', *args)


def get_ports(type='Ethernet'):
    """Return all devices of type (Ethernet, AirPort)"""
    profile = SystemProfile('Network')
    return [x for x in profile if x['type'] == type]


def set_wifi_power(on=True):
    """Set AirPort power to on (True) or off (False)"""
    state = 'on' if on else 'off'
    for i in get_ports('AirPort'):
        networksetup('-setairportpower', i['interface'], state)


def disable_wifi(port='en1'):
    networksetup('-setairportpower', port, 'off')
    networksetup('-setnetworkserviceenabled', 'Wi-Fi', 'off')


def get_wifi_power():
    """Get AirPort power state."""
    results = []
    for i in get_ports('AirPort'):
        iface = i['interface']
        r = networksetup('-getairportpower', iface)
        results.append(r.split(': ')[1])

    return 'On' in results


def is_wired(primary=False):
    """Do we have an "active" Ethernet connection?"""
    for p in get_ports('Ethernet'):
        try:
            r = check_output('/sbin/ifconfig', p['interface'])
        except Exception as e:
            raise Exception('Failed to get interface status: %s' % e)

        active = 'status: active' in r
        return get_primary(p['interface']) if primary else active


def is_wireless():
    return not is_wired()


def get_primary(port=None):
    """Return device node of primary network interface"""
    try:
        route = check_output('/sbin/route', 'get', 'default').split('\n')
    except Exception as e:
        raise Exception('Failed to get default route: %s' % e)

    for i in [x for x in route if 'interface: ' in x]:
        p = i.split(': ')[1]
        return p == port if port else p


def flush_dns():
    """Flush the DNS cache."""
    kill('mDNSResponder', 'HUP')


def get_computer_name():
    """Return the Computer Name of this Mac"""
    return networksetup('-getcomputername')


def set_computer_name(name, hostname=True):
    networksetup('-setcomputername', name)
    if hostname:
        set_hostname(name)


def set_hostname(name):
    systemsetup('-setlocalsubnetname', name)


def fix_computer_name(name):
    """Removes the (\d) from the computer name and local hostname"""
    return re.sub(r'\s\(\d+\)', '', name)
