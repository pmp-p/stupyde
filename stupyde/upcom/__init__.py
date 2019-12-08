import os
import time as Time
import json

ESP32 = 'ESP-32'

ESP8266 = 'ESP-8266'


def run(port,code, popen=True):
    from serial import Serial
    with Serial(port, 115200) as esp:
        #esp.write('
        esp.write( b'\x01' )
        esp.write( bytes('code = %r\n' % code ,'latin1' ) )
        esp.write( b'exec(code,globals(),globals());print("\x06")\n' )
        esp.write( b'\x04\x02')
        esp.flush()

        cdown = 8000
        if popen:
            Time.sleep(0.1)
            buf = []
            eot = False
            while cdown:
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
                    cdown -= 1
                    Time.sleep(0.001)
            else:
                print('52: %s timeout to run cmd' % port)
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

    def sha256(f,block=512):
        import hashlib as uhashlib
        import binascii as ubinascii
        h = uhashlib.sha256()
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

    def precompile(fat,mpy):
        global SRC,MPY
        path = ( '%s/tmp' % SRC).replace('//','/')
        cache = '%s/mpy' % path
        print(' - compiler cache is %s' % cache )

        if not os.path.isdir(path):
            os.mkdir(path)
            with open( cache, 'wb') as f:
                f.write( json.dumps( {} ).encode('utf-8') )

        try:
            with open( cache, 'rb') as f:
                old_fat = json.loads( f.read().decode('utf-8') )
        except FileNotFoundError:
            #cache folder tmp/ content was erased
            old_fat = {}

        for fn in list(fat.keys()):

            if fn in ('boot.py','main.py','assets/repl.py'):
                print(' * skipping %s *' % fn)
                continue

            dest = '{}/{}.mpy'.format(path, fat[fn] )
            comp = ('{} {}/{} -o {} >/dev/null'.format( MPY,SRC, fn , dest )).replace('//','/')

            if os.system(comp):
                print("\n\t^ error in <%s>" % fn)
                print('_'*30)
                print()
                continue

            #replace source by mpy = sha256 , add dest mpy name = tmp mpy file
            fat.pop(fn)
            fn = fn[:-2]+'mpy'
            fat[fn] = sha256(dest)
            mpy[fn] = dest

    def compiled(fat, fn):
        global SRC
        path = ( '%s/tmp' % SRC).replace('//','/')
        dest = '{}/{}.mpy'.format(path, fat[fn] )
        if os.path.isfile(dest):
            return dest
        return ''

    def upcom(board_script, board, port):

        global SRC,MPY

        MPY = os.getenv('MPY',False)

        #file table for board to sum
        fat = {}

        mpy = {}


        for fn in os.popen("find -L %s|grep .py$ |grep -v %s/local/" % (SRC,SRC) ).readlines():
            fn = fn.strip('./ \n\r\t')
            if not os.path.isfile(fn):
                continue
            if fn.endswith('.mpy'):
                continue
            if not fn.endswith('.py'):
                continue

            fat[fn.split( SRC, 1)[-1]] = sha256(fn)

        if MPY:
            print("  -> will precompile files with %s" % MPY )
            precompile(fat,mpy)

        print(' - Sending file table to board via {}'.format(RUN_SCRIPT) )
        with open(RUN_SCRIPT, "wb") as fastupd:
            source = open(board_script,'rb').read().decode('utf-8') % { 'fat': repr(fat), 'src': SRC }

            fastupd.write( source.encode('utf-8') )

        print(f"\nBoard {board}@{port} will update for :")
        print("-" * 20,"\n\n")

        updates = []

        if board in (ESP32,):
            code =  open(RUN_SCRIPT,'rb').read().decode('utf-8')

            for l in run(port, code ):
                l = l.strip()
                if l.startswith("~ "):
                    print('\t',l )
                    updates.append(SRC + l.strip("~ "))
            Time.sleep(0.6)
            print()

            print('Syncing files ...')

            for upd in updates:
                print(upd)
                dst = upd.split(SRC, 1)[-1]
                if dst.endswith('.mpy'):
                    upd =  mpy[dst]
                    print('MPY=> ',dst)

                cp(upd,dst,**{ 'port':port, '-v': True } )

                #FIXME: wait ack from board like for run+popen
                Time.sleep(0.1)

            Time.sleep(0.1)
            [ run(port,  b"\x04\x02__import__('machine').reset()\n" , popen=False) ]

        else:
            Time.sleep(1)
            print("#FIXME: timeout here on bad reset ?")
            Time.sleep(1)

            for l in os.popen("ampy run %s" % RUN_SCRIPT):
                l = l.strip()
                if l.startswith("~ "):
                    print('\t',l )
                    l = l.strip('~ \r\n')
                    updates.append(l)
                else:
                    print(l)

            Time.sleep(0.6)
            print()


            print('syncing files ...')
            for upd in updates:
                dst = upd
                if upd.endswith('.mpy'):
                    upd =  mpy[upd]
                    print('MPY=> ',dst)
                    os.system("ampy put %s /%s" % (upd,dst) )
                else:
                    print(upd,' => ',dst)
                    os.system("ampy put %s%s /%s" % (SRC,upd,dst) )
                Time.sleep(0.01)

            print('\n\nAll files sent, reset Board ...')
            with open( RESET_SCRIPT,'wb') as f:
                f.write(b'''try:__import__('os').remove('/osdebug')
except:pass
__import__('machine').reset()
''')
            os.system('ampy run %s' % RESET_SCRIPT)
            Time.sleep(0.2)








#
