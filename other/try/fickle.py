# just testing, doesn't work yet

import copy_reg, marshal, types
def code_unpickler(data): return marshal.loads(data)
def code_pickler(code): return code_unpickler, (marshal.dumps(code),)
copy_reg.pickle(types.CodeType, code_pickler, code_unpickler)

def function_unpickler(code, name, defaults):
    return types.FunctionType(code, globals(), name, defaults)
def function_pickler(func):
    return function_unpickler, (func.func_code, func.__name__, func.func_defaults)
copy_reg.pickle(types.FunctionType, function_pickler, function_unpickler)

def foo(x):
    print "==", x
    return x*2
import pickle
print pickle.dumps(foo)
print pickle.dumps(lambda:"abc")
