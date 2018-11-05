import os
import time as Time
import json

ESP32 = 'ESP-32'

ESP8266 = 'ESP-8266'

def run(port,code, popen=True):
    from serial import Serial
    with Serial(port, 115200) as esp:
        esp.write( b'\x01' )
        esp.write( bytes('code = %r\n' % code ,'latin1' ) )
        esp.write( b'exec(code,globals(),globals());print("\x06")\n' )
        esp.write( b'\x04\x02')
        esp.flush()
        if popen:
            Time.sleep(0.1)
            buf = []
            eot = False
            while True:
                incoming = esp.read(esp.in_waiting).decode('utf-8')
                if incoming:
                    buf.append( incoming )

                    incoming = ''.join( buf )
                    buf.clear()

                    if incoming.count( chr(6) ):
                        #flush noises
                        eot=True

                    while incoming.count('\r\n'):
                        head,incoming = incoming.split('\r\n',1)
                        yield head

                    if incoming:
                        buf.append(incoming)

                    if eot:
                        if len(buf):
                            yield ''.join( buf)
                        break
                else:
                    Time.sleep(0.001)
        esp.reset_input_buffer()



def cp(args_filename, args_destination, **kw):
    from serial import Serial
    from zlib import compress
    with Serial( kw.get('port'), 115200) as esp:

        if '-v' in kw:
            print(args_filename,' => ',args_destination)

        esp.write( b'\x01' )
        with open(args_filename, 'rb') as source_file:
            esp.write( bytes('data = %r\n' % compress(source_file.read()) ,'latin1' ) )
        esp.flush()

        esp.write( bytes( '''
from uzlib import decompress
with open('%s', 'wb') as target_file:
    target_file.write(decompress(data))
print("\x06")
''' % args_destination ,'latin1') )
        esp.write( b'\x04' )
        esp.write( b'\x02' )
        esp.flush()
        while True:
            incoming = esp.read(esp.in_waiting).decode('utf-8')
            if incoming:
                if incoming.count( chr(6) ):
                    break
            else:
                Time.sleep(0.001)
        esp.reset_input_buffer()


def TMP(name):
    return '/'.join( ( os.getenv('TMP','/tmp') , name ) )

SRC = os.getenv('WORKDIR')

if SRC is None:
    print("WORKDIR is not set, i don't know what folder to sync")
else:

    SRC = SRC.strip('.\r\n/ ')+"/"
    RUN_SCRIPT = TMP("fastupd.py")
    RESET_SCRIPT = TMP("fastboot.py")

    def sha1(f,block=512):
        import hashlib as uhashlib
        import binascii as ubinascii
        h = uhashlib.sha1()
        if isinstance(f, str):
            try:
                f = open(f, "rb")
            except OSError:
                f = None
        while f:
            data = f.read(block)
            if data:
                h.update(data)
            else:
                break
        if f:
            f.close()
        return ubinascii.hexlify(h.digest()).decode()  # .lower()


    def upcom(board_script, board, port):




        #file table for board to sum
        fat = {}

        for fn in os.popen("find -L %s|grep .py$" % SRC).readlines():
            fn = fn.strip()
            fat[fn.rsplit( SRC, 1)[-1]] = sha1(fn)

        print(' - Sending file table to board via {}'.format(RUN_SCRIPT) )
        with open(RUN_SCRIPT, "wb") as fastupd:
            fat = open(board_script,'rb').read().decode('utf-8') % { 'fat': repr(fat), 'src': SRC }

            fastupd.write( fat.encode('utf-8') )

        print(f"\nBoard {board}@{port} will update for :")
        print("-----------------------\n\n")

        updates = []

        if board == ESP32:
            print()
            code =  open(RUN_SCRIPT,'rb').read().decode('utf-8')

            for l in run(port, code ):
                l = l.strip()
                if l.startswith("~ "):
                    print('\t',l )
                    updates.append(SRC + l.strip("~ "))

            Time.sleep(0.8)
            print()
            print('Syncing files ...')
            for upd in updates:
                dst = upd.rsplit( SRC, 1)[-1]
                cp(upd,dst,**{ 'port':port, '-v': True } )

                #FIXME: wait ack from board like for run+popen
                Time.sleep(0.1)

            [ run(port, "__import__('machine').reset()" , popen=False) ]

        else:
            for l in os.popen("ampy run %s" % RUN_SCRIPT):
                l = l.strip()
                if l.startswith("~ "):
                    print('\t',l )
                    updates.append(SRC + l.strip("~ "))
                else:
                    print(l)

            Time.sleep(0.8)
            print()
            print('syncing files ...')
            for upd in updates:
                dst = upd.rsplit( SRC, 1)[-1]
                print(upd,' => ',dst)
                os.system("ampy put %s /%s" % (upd,dst) )
                Time.sleep(0.02)

            print('\n\nAll files sent, reset Board ...')
            with open( RESET_SCRIPT,'wb') as f:
                f.write(b'''__import__('machine').reset()''')
            os.system('ampy run %s' % RESET_SCRIPT)
            Time.sleep(0.2)

