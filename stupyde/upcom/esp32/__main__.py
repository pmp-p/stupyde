import os,sys

from . import *

port = os.getenv('AMPY_PORT')
if port is None:
    port = glob.glob('/dev/ttyUSB*')[-1]
    print('using autodetected port %s' % port )

if 'test' in sys.argv:
    for l in run(port,'import sys;print("{%s}"%sys.platform)'):
        print(l)

else:
    parser = ArgumentParser(
        description=(
            'Upload a file to ESP8266/ESP32 using serial REPL, '
            'requires your ESP32 to currently be running the REPL and not your own program'
        )
    )
    parser.add_argument(
        'filename',
        type=str,
        help='Full path to source file',
    )
    parser.add_argument(
        'destination',
        type=str,
        help='Name of target file',
        nargs='?',
    )

    copy(  parser.parse_args() , port )
