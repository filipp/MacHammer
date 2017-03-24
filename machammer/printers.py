# -*- coding: utf-8 -*-

from .functions import call, popen, check_output, log

LPSTAT = '/usr/bin/lpstat'
LPADMIN = '/usr/sbin/lpadmin'


def reset():
    """Reset this printing system."""
    pass


def delete_printer(printer):
    log('Deleting printer %s' % printer)
    return call(LPADMIN, '-x', printer)


def delete_printers():
    """Delete all print queues on the system."""
    for p in check_output(LPSTAT, '-p').split("\n"):
        printer = p.split(' ')[1]
        delete_printer(printer)


def add_printer(printer, options={}, delete=True):
    """Add a printer queue.

    A printer is a tuple (name, PPD path, LPD address)
    """
    if delete:
        delete_printer(printer[1])

    name = printer[0]
    ppd = '/Library/Printers/PPDs/Contents/Resources/%s' % printer[1]

    # Install the printer
    cmd = ['/usr/sbin/lpadmin',
           '-p', name.replace(' ', '-'),
           '-L', name[0:2],
           '-D', name,
           '-v', 'lpd://%s' % printer[2],
           '-P', ppd,
           '-E',
           '-o', 'printer-is-shared=false',
           '-o', 'printer-error-policy=abort-job']

    for option in options.keys():
        cmd.append('-o')
        cmd.append(str(option) + '=' + str(options[option]))

    return popen(cmd)
