'''
ESP32 upload tool by The Cheaterman, py3.7 version pmpp ( blonde beer for me )
WTFPL license (although it's very much compatible with beerware)
'''

from argparse import ArgumentParser
from os.path import basename

from textwrap import dedent
from zlib import compress
import glob
import time as Time


from serial import Serial

def run(port,code, raw=True):
    from serial import Serial
    with Serial(port, 115200) as esp:
        if raw:esp.write( b'\x01' )
        esp.write( bytes('code = %r\n' % code ,'latin1' ) )
        esp.write( b'exec(code,globals(),globals());print("\x06")\n' )
        if raw:esp.write( b'\x04\x02')
        esp.flush()
        Time.sleep(0.1)
        buf = []
        eot = False
        while True:
            incoming = esp.read(esp.in_waiting).decode('utf-8')
            if incoming:
                print("%r"%incoming)

                if incoming.count( chr(6) ):
                    print('\n\nEOT found\n\n')
                    eot=True

                if incoming.count('\n'):
                    head,trail = incoming.split('\n',1)
                    buf.append(head)
                    yield ''.join( buf)
                    buf = [trail]
                else:
                    buf.append(head)

                if eot:
                    if len(buf):
                        yield ''.join( buf)
                    break
            else:
                Time.sleep(0.01)



def copy(args,port):
    with Serial(port, 115200) as esp:
        esp.write( b'\x01' )
        with open(args.filename, 'rb') as source_file:
            esp.write( bytes('data = %r\n' % compress(source_file.read()) ,'latin1' ) )
        esp.write( bytes( dedent('''
            from zlib import decompress
            with open('%s', 'wb') as target_file:
                target_file.write(decompress(data))
        ''' % (args.destination if args.destination else basename(args.filename))
        ).strip() + '\n' ,'latin1') )
        esp.write( b'\x04' )
        esp.write( b'\x02' )


