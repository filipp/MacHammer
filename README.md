### Introduction

`machammer` is library/microframework for Macintosh system administration. The idea is to provide a set of common, often-used functions for admins to build their own management tools.


### System Requirements

- OS X (tested with 10.11)


### Example

In this example we will create an initial installation and setup script for a new Mac. We will install some configuration profiles and packages, copy some apps and configure our print queues.

We will assume you have a fileshare where you also keep your installation files. In this example, the fileshare is mounted on `/Volumes/MyShare` and all the installation resources are in a subdirectory called `Installation`.

```python
import os
from machammer import functions as mh # Import general-purpose admin commands
from machammer import printers # Import printer-related commands

APP_ROOT = '/Volumes/MyShare/Installation'
mh.display_notification('Starting installation')

# Configure the Mac to use our in-house software update server
mh.install_profile(os.path.join(APP_ROOT, 'Settings_for_SoftwareUpdate.mobileconfig'))

# Install all Software Updates. This may reboot your machine (provide restart=False, if you want to avoid that)
mh.install_su()

myprinter = ('LaserWriter 8500', 'LaserWriter8500.ppd', 'lw.example.com',)
printers.add_printer(myprinter)

# Install Java. mount_and_install takes 2 arguments - the path to the disk image and the path to installation package on the mounted volume
mh.mount_and_install(os.path.join(APP_ROOT, 'jre-8u101-macosx-x64.dmg'), 
                     'Java 8 Update 101.app/Contents/Resources/JavaAppletPlugin.pkg')

# Install Microsoft Office. mount_image returns the path to the new mountpoint
p = mh.mount_image('/Volumes/MyShare/Installation/Office2016.dmg')
mh.install_package(os.path.join(p, 'Microsoft_Office_2016_15.23.0_160611_Installer.pkg'))

# Install ArchiCAD 19
p = mh.mount_image(os.path.join(APP_ROOT, 'ArchiCAD/19/AC19-3003-INT.dmg'))
mh.exec_jar(os.path.join(p, '/ArchiCAD Installer.app/Contents/Resources/Java/archive.jar'), 'localadmin')

# Install Viscosity on laptops
if mh.is_laptop():
    p = mh.mount_image('/Volumes/MyShare/Installation/Viscosity 1.6.6.dmg')
    mh.copy_app(os.path.join(p, 'Viscosity.app'))

mh.display_notification('Installation complete!')
sys.exit(0)
```

Save that in `install.py` (or whatever you want) and just run with `sudo python install.py`. I would recommend putting the installation script alongside with machammer itself on the fileshare so you don't have to install anything on the client machine to be able to run it.

`install.py` serves two important purposes - first and foremost, it allows you to get machines up and running quickly and with minimal user-intervention (depending on the payload). Secondly, it also serves as your official configuration documentation!

    Pro tip: put install.py under version control!

### Reusing admin tasks

Just name your admin tasks as functions. For example, this will install AutoCAD LT 2016 and all the patches:

```python
def install_autocad():
    mh.mount_and_install(os.path.join(APP_ROOT, 'AutoCAD/Autodesk AutoCAD LT 2016 for Mac Installation.dmg'),
                         'Install Autodesk AutoCAD LT 2016 for Mac.pkg')
    for x in xrange(1, 4):
        mh.mount_and_install(os.path.join(APP_ROOT, 'AutoCAD/AutoCADLT2016Update%d.dmg' % x),
                             'AutoCADLT2016Update%d.pkg' % x)
```

Since this is all just pure Python, feel free to put your Linux admin tasks in there as well. For instance, to update all your Maxwell rendernodes:

```python
def update_render_nodes():
    for n in range(1, 11):
        installer = os.path.join(APP_ROOT, 'Maxwell/Maxwell_3.2.1.5')
        subprocess.call('ssh', 'admin@render%d.example.com' % d, 'killall mxnetwork;' + installer)
```

The above Linux example assumes you've configured your nodes to mount the fileshare the same way as your Macs (under /Volumes). You can run it from your admin Mac.


### Making install.py more "modular"

Sometimes you just want to run parts of `install.py`. By adding this snippet to the end of `install.py`:


```python
if __name__ == '__main__':
    if len(sys.argv) > 1:
        for x in sys.argv[1:]:
            try:
                locals()[x]()
            except KeyError as e:
                mh.log('Function not found: %s' % x)

        sys.exit(0)
```

... you can call your named admin tasks (functions) simply providing their names on the command line:


```bash
$ python install.py install_autocad update_render_nodes
```


### system_profiler

`machammer` includes `system_profiler` - a small wrapper around OS X's `system_profiler (1)` tool. It provides a simple API for accessing system profile information as well as caching to improve performance (especially when dealing with application profile data).


#### Usage

Simple example to find and list all versions of ArchiCAD 19:

```python
import system_profiler
results = system_profiler.find('Applications', '_name', 'ArchiCAD 19')
print([x['version'] for x in results])
['19.0.0 R1 FIN (6006)']
```

Check `tests.py` for more usage examples.


### FAQ

* Q: Why not use Bash?
* A: It's true that most of this stuff is just glue to various command line utilities and using Bash might save some keystrokes, but Python is just a much better programming language with an actual standard library. 
* Q: Why not use Munki?
* A: No reason whatsoever. Munki is great and you should totally use it, if it works for you. I just prefer to read and write code than learn a new XML syntax. For me personally, it was difficult to "start small" with Munki - there's a lot you have to learn to get started. Also, there are plenty of apps out there that don't conform to the standard PKG/app bundle format (like the ArchiCAD example above) and your best bet at tackling those is just plain-old scripting. To paraphrase Einstein - an installation tool might take you from A to B, but scripting can take you anywhere. :-)


### License

    Copyright (c) 2016 Filipp Lepalaan

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
