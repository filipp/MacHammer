from .functions import tell_app



def get():
    return tell_app('System Events', 'get name of current screen saver')


def set(name):
    return tell_app('System Events', 'set current screen saver to (get screen saver named "%s")' % name)


def start():
    return tell_app('System Events', 'start current screen saver')


def stop():
    return tell_app('System Events', 'stop current screen saver')
