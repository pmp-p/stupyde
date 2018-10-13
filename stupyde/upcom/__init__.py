import os
import time as Time
import json

def TMP(name):
    return '/'.join( ( os.getenv('TMP','/tmp') , name ) )

SRC = os.getenv('WORKDIR')
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


def upcom(board_script):

    #file table for board to sum
    fat = {}

    for fn in os.popen("find -L %s|grep .py$" % SRC).readlines():
        fn = fn.strip()
        fat[fn.rsplit( SRC, 1)[-1]] = sha1(fn)

    print(' - Sending file table to board via {}'.format(RUN_SCRIPT) )
    with open(RUN_SCRIPT, "wb") as fastupd:
        fat = open(board_script,'rb').read().decode('utf-8') % { 'fat': repr(fat), 'src': SRC }

        fastupd.write( fat.encode('utf-8') )
        #print(fat, file=fastupd )


    print("\nBoard will update for :")
    print("-----------------------\n\n")
    updates = []
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

