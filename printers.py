# -*- coding: utf-8 -*-

import subprocess


def delete_printers():
    for p in subprocess.check_output(['lpstat', '-p']).strip().split("\n"):
        subprocess.call(['lpadmin', '-x', p[1]])


def add_printer(printer, options={}):
    """
    Adds a printer
    A printer is a tuple (name, PPD path, LPD address)
    """
    cmd = ['/usr/sbin/lpadmin', '-x', printer[1]]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (lpadminxOut, lpadminxErr) = proc.communicate()

    # Install the printer
    cmd = ['/usr/sbin/lpadmin',
           '-p', printer[0].replace(' ', '-'),
           '-L', printer[0][0:2],
           '-D', printer[0],
           '-v', 'lpd://%s' % printer[2],
           '-P', '/Library/Printers/PPDs/Contents/Resources/%s' % printer[1],
           '-E',
           '-o', 'printer-is-shared=false',
           '-o', 'printer-error-policy=abort-job']

    for option in options.keys():
        cmd.append("-o")
        cmd.append(str(option) + "=" + str(options[option]))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (res, err) = proc.communicate()

    if err:
        raise Exception(err)
