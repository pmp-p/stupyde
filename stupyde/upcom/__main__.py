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


code="""
__import__('machine').RTC().datetime({})
try:
    use.aio.__class__.paused=True

except:
    pass
print("[%s]" % __import__('sys').platform)
""".format(tm)


for testboard in run(port,code):

    if testboard.count('[esp32]'):
        board= ESP32
        sync_script = '/sync/esp32.py'
        break

    elif testboard.count('[esp8266]'):
        board = ESP8266
        sync_script = '/sync/esp8266.py'
        break
else:
    print('board not recognized or not running micropython')
    board = '?'

#esp8266 may need serious ram purge before receiving more code
if board == ESP8266:
    code ="""
__import__('gc').collect()
for k in dir(__import__('builtins')):
    try:delattr(__import__('builtins'),k)
    except:pass
for k in dir():
    try:delattr(__import__(__name__),k)
    except:pass
__import__('sys').modules.clear()
__import__('gc').collect()
print("~ Free RAM :", __import__('gc').mem_free() )
print('\x06')
"""
    for purge in run(port,code):
        if purge.count('~'):
            print(purge)


#give time to aio for stopping
Time.sleep( float( os.getenv('AIO_EXIT',0.5) ) )

print(f" - Syncing board {board} for wordir [",SRC,"]" )

upcom( __file__.rsplit('/',1)[0] + sync_script, board, port )

print('>>> ',end='')

