import sys,gc
import utime as Time
import uos as os

print('Begin update list', gc.mem_free() )

fat = %(fat)s

def sha256(f,block=512):
    import uhashlib,ubinascii
    h = uhashlib.sha256()
    if isinstance(f, str):
        try:
            f = open(f,'rb')
        except OSError:
            f = None
    while f:
        data = f.read(block)
        if data:
            h.update(data)
        else:break
    if f:f.close()
    return ubinascii.hexlify(h.digest()).decode()

while fat:
    k,v = fat.popitem()
    if k.count('/'):
        dirs = k.split('/')
        dirs.pop()
        dirs.insert(0,'')
        try:
            os.stat( '/'.join(dirs) )
            notfound = False
        except:
            notfound = True
        if notfound:
            cpath=[]
            while dirs:
                cpath.append( dirs.pop(0) )
                mkd='/'.join(cpath)
                try:
                    os.stat(mkd)
                except:
                    print("Created :", mkd)
                    os.mkdir( mkd )

    if v!=sha256(k): print('~',k)

gc.collect()
print('End update list',sys.platform,gc.mem_free() )
print('\x06')
