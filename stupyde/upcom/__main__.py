print("UPCOM\n\nmicropython tool for UART reachable boards, License MIT http://github.com/pmpp-p")
print("="*80,end="\n\n")


from . import *

port = os.getenv('AMPY_PORT')
if port is None:
    port = glob.glob('/dev/ttyUSB*')[-1]
    print('using autodetected port %s' % port )


import time as Time
tm=Time.gmtime()

tm = tm[0:3] + (0,) + tm[3:6] + (0,)

# cut asyncio / soc debug and sync time

code="""
import sys
try:__import__("esp").osdebug(None)
except:pass

__import__('machine').RTC().datetime({})

try:
    aio.paused=True
except:
    try:
        use.lives=False
        __import__('asyncio').get_event_loop().close()
    except:
        try:
            __import__('uasyncio').get_event_loop().close()
        except:
            pass

print("[%s]" % sys.platform)

import gc
gc.collect()
ram = gc.mem_free()
print("~ Free RAM :", gc.mem_free() )
print('\x06')
if sys.platform=='esp8266':
    open('/osdebug','wb').close()
    __import__('machine').reset()
""".format(tm)

print()
print("Use ctrl+c once or twice to force REPL if using hard asyncio loop or blocking read")

board = '?'
res =  list(run(port,code))
for testboard in res:
    if testboard.startswith('~'):
        print(testboard)
        break

    if testboard.count('[esp32]'):
        board= ESP32
        sync_script = '/sync/esp32.py'
        break

    elif testboard.count('[esp8266]'):
        board = ESP8266
        sync_script = '/sync/esp8266.py'
        break
else:
    print("board not recognized", res)

if board == "?":
    import sys
    print('Error: board not recognized, not running micropython or busy looping', file=sys.stderr)
    raise SystemExit(1)

if board == ESP8266:
    Time.sleep(2)

##give time to aio for stopping
#Time.sleep( float( os.getenv('AIO_EXIT',0.5) ) )

print(f" - Syncing board {board} for wordir [",SRC,"]" )

upcom( __file__.rsplit('/',1)[0] + sync_script, board, port )

print('>>> ',end='')

