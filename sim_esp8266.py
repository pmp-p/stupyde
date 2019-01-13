#boot.py
import sys, gc, builtins

#uos on esp has "listdir"
import os as os

import ujson as json

builtins.sys = sys

import stupyde.fixes

class config:
    # FIXME: use gh by default
    srv = "http://192.168.1.66/mpy/%s/" % sys.platform
    SSID = "SSID"
    WPA = ""
    IP = "0.0.0.0"
    RAM=32768*4
    BPS=115200


if '/lib' in sys.path:
    sys.path.remove('/lib')
sys.path.append('/assets')

import xpy.builtins
del sys.modules['xpy.builtins']
use.gc()


def init():
    import time as Time

    builtins.Time = Time
    global core

    def isDefined(sym, ns=None):
        try:
            return (getattr(__import__(ns or __name__), sym, 0) and 1) or (
                eval(sym,globals()) or 1
            )
        except NameError:
            return False

    def await_(f):
        try:
            list(f)
        except StopIteration as e:
            return e.args[0]

    for m in (os, sys, builtins, isDefined, await_):
        setattr(builtins, m.__name__, m)

    if 'aio' in os.listdir():
        import xpy.aio
        del sys.modules['xpy.aio.aio_upy']
        del sys.modules['xpy.aio']
        del xpy.aio


init()
del init, sys.modules['xpy']
gc.collect()

reboot = ld('klib.reboot')
with dlopen('klib') as klib:
    builtins.klib = klib
    builtins.Pin = klib.Pin
    builtins.fopen = klib.fopen



#main.py

if use.IP[-1]=='0':
    __file__ = 'assets/repl.py'
    with open(__file__,'rb') as f:
        __code__ = f.read()
else:
    __file__ = ''.join( (use.srv, use.IP,'.py',) )
    __code__ = fopen(__file__).read()

print(__file__,'='*79,sep='\n')

use.gc()


#global __code__, __file__
__code__ = compile( __code__ , __file__, 'exec')
exec(__code__,globals(),globals())
__code__ = __file__
use.gc()
if use.aio:
    use.aio.run()
else:
    try:
        await_(__main__())
    except KeyboardInterrupt:
        pass








