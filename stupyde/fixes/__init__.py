import sys
import builtins
import stupyde

def fixme(module):
    module = '%s.%s' % ( __name__ , module )
    __import__( module )
    module = eval(module)
    module.__file__ = '<fixes>'
    module.__name__ = module.__name__.rsplit('.',1)[-1]
    sys.modules[module.__name__] = module
    setattr( builtins, module.__name__, module )


fixme('micropython')

fixme('machine')

fixme('contextlib')

fixme('contextvars')
