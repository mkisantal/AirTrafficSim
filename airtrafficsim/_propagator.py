import ctypes
from numpy.ctypeslib import ndpointer
import numpy as np
import os


module_path = os.path.dirname(os.path.abspath(__file__))
cpp_lib = ctypes.CDLL(os.path.join(module_path, 'propagator.so'))

cpp_lib.propagate.argtypes = (ndpointer(dtype=ctypes.c_float, shape=(3,)),
                              ndpointer(dtype=ctypes.c_float, shape=(3,)),
                              ctypes.c_float, ctypes.c_float, ctypes.c_float,)

c_propagator = cpp_lib.propagate


if __name__ == "__main__":
    pos = np.array([1000, 5000, 300], dtype=np.float32)
    vel = np.array([100, 100, 0], dtype=np.float32)

    dt = float(1.0)
    turn_rate = float(45)
    climb_rate = float(55.0)

    print(pos, vel)

    cpp_lib.propagate(pos, vel, dt, turn_rate, climb_rate)

    print(pos, vel)
