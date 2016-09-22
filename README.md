### Introduction

`machammer` is library/microframework for Macintosh system administration. The idea is to provide common, often-used functions for admins to build their own management tools.


### System Requirements

- OS X


### system_profiler

machammer includes `system_profiler` - a simple wrapper around OS X's `system_profiler (1)` tool. It provides a simple API for accessing system profile information as well as caching to improve performance (especially when dealing with application profile data).


#### Usage

Simple example to find and list all versions of ArchiCAD 19:

```python
import system_profiler
results = system_profiler.find('Applications', '_name', 'ArchiCAD 19')
print([x['version'] for x in results])
['19.0.0 R1 FIN (6006)']
```

Check `tests.py` for more usage examples.


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
