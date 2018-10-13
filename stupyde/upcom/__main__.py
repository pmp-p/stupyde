print("UPCOM\n\nmicropython tool for ampy reachable boards, License MIT http://github.com/pmpp-p")
print("="*80,end="\n\n")


from . import *
print(" - Syncing board for wordir [",SRC,"]" )

upcom( __file__.rsplit('/',1)[0] + '/sync/esp8266.py' )

print('>>> ',end='')

