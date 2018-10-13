import sys
import utime as Time
import uos as os

fat = %(fat)s

def sha1(f,block=512):
    import uhashlib,ubinascii
    h = uhashlib.sha1()
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

print(sys.platform,'update list for source tree %(src)s :',sep=' : ')
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
                    print("creating folder : ", mkd)
                    os.mkdir( mkd )
            Time.sleep(0.5)
            #print("having ENOENT with folder path ? then just retry again")

    if v != sha1(k):
        print('~',k)

print(sys.platform,'end update list',sep=' : ')
