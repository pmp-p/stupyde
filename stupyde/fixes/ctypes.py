import uctypes as self
import struct


def __getattr__(attr):
    return getattr(self, attr)


def pointer(v):
    return struct.pack("P", v)


class PTYPE(str):
    pass


def sizeof(cstruct, setval=0, v=0):


    if isinstance(cstruct, tuple):
        if isinstance(cstruct[0], tuple):
            cumul=0
            for arg in cstruct:
                argsize = sizeof(arg)
                if not argsize:
                    raise Exception('invalid struct')
                cumul += argsize
            return cumul
        return abs(cstruct[1])

    if cstruct == type(None):
        if v:print(cstruct,"is None")
        return 0

    if isinstance(cstruct, (CFUNCTYPE, tuple )):
        if v:print(cstruct,"is CFUNC")
        return 0

    if isinstance(cstruct, str):
        # can only be a POINTER()
        setval = 4
        cname = str(cstruct)
    else:
        sz = PT.sizeof(cstruct)
        if sz:
            return sz
        cname = cstruct.__name__

    st = PT.cstructs.setdefault(cname, {})
    sz = st.setdefault("struct", setval)
    if not sz and setval:
        st["struct"] = setval
    return sz


def struct_size_get(cstruct, verbose=0):
    cumul=sizeof(cstruct)
    if cumul:
        return cumul

    # walk was not complete
    if verbose:print(cstruct.__name__)
    for (fname, ftype) in cstruct._fields_:
        if verbose:print('  ',fname, end=" -> ")
        sz = sizeof(ftype)
        if not sz:
            if verbose:print("N/A {}".format( repr(ftype) ), sizeof(ftype,v=1) )
            break
        cumul += sz
        if verbose:print(sz)
    else:
        if verbose:print('FINAL!')
        return sizeof(cstruct, setval=cumul)
    return 0


class PT:
    _fields_ = ()

    types = {}
    cstructs = {}

    @staticmethod
    def sizeof(cls):
        return ffisign.get(cls,(0,0,))[1]

    def __init__(self, iptr=PTYPE("void"), cptr=-1):
        self.cptr = cptr
        self.cref = 0
        self.ctype = iptr

        # Invalid pointer by default
        if isinstance(iptr, PTYPE):
            self.sizeof = 4
        else:
            self.sizeof = sizeof(iptr)

            if isinstance(iptr, type(PT)):
                struct_size_get(iptr)
                print("TODO:", iptr.__name__, len(iptr._fields_), self.sizeof)
                iptr = iptr.__name__

            if isinstance(iptr, str):
                print("TODO: ", iptr, self.cptr, self.sizeof)
            else:
                # raw pointer
                print("44:warning raw pointer")
                self.cptr = iptr

        self.sizeof = 1

    def __int__(self):
        if not self.cref and (self.cptr < 0):
            raise Exception("Pointer address not set")
        # TODO this only handle const ptr
        if not self.cptr:
            self.cptr = struct.unpack("P", self.cref)[0]

        return self.cptr

    value = __int__

    def __add__(self, v):
        return int(self) + (v * self.sizeof)

    def byref(self):
        if not self.cref:
            if self.cptr < 0:
                # promote to NULL pointer
                self.cptr = 0
            if self.sizeof==4:
                self.cref = struct.pack("P", self.cptr)
            else:
                sz = sizeof(self.ctype)
                alloc =  "{}B".format(sz)
                print(self.ctype,'allocated', alloc )
                self.cref = struct.pack(alloc, 0)
        return self.cref

    def __getattr__(self, attr):
        print(self,attr)


    def __repr__(self):
        return "^{}".format(self.__int__())


def POINTER(ctype):
    if isinstance(ctype, tuple):
        cname = "%s%s" % ctype
        sign = ctype[0]
        sz = ctype[1]
    else:
        sz = 4
        sign = "P"
        if isinstance(ctype, str):
            cname = ctype
        else:
            cname = ctype.__name__

    if not cname in PT.types:
        c = PTYPE(cname)
        ffisign[c] = (sign, sz)
        PT.types[cname] = c
    return PT.types[cname]


class c_void_p(PT):
    pass


class c_char_p(PT):
    pass


class Structure(PT):
    _fields_ = []


py_object = "py_object"

c_char = ("c", 1)
c_uint8 = ("B", 1)
c_int8 = ("b", -1)
c_uint16 = ("H", 2)
c_int16 = ("H", -2)
c_uint32 = c_uint = ("I", 4)
c_int32 = c_int = ("i", -4)
c_size_t = ("N", 4)
c_ulong = c_ulonglong = c_uint64 = ("Q", 8)
c_long = c_longlong = c_int64 = ("q", -8)
c_float = ("f", -4)
c_double = ("f", -8)

ffisign = {
    type(None): ("v", 0),
    c_void_p: ("p", 4),
    c_char_p: ("s", 4),
    int: ("i", 4),
    float: ("f", 4),
    # Structure: ('p',0),
}


class CFUNCTYPE:
    __name__ = "CFUNCTYPE"

    def __init__(self, *argv, **kw):
        self.argv = argv


def memmove(*argv, **kw):
    print("memmove", argv, kw)
    raise Exception("N/I")


def string_at(*argv, **kw):
    print("string_at", argv, kw)
    raise Exception("N/I")


class Union:
    _fields_ = []


def _Pointer(*argv, **kw):
    print("_Pointer", argv, kw)
    raise Exception("N/I")
