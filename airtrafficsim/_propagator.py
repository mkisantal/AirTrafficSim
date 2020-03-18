import ctypes
from numpy.ctypeslib import ndpointer
import numpy as np
import os


# Loading C++ library
module_path = os.path.dirname(os.path.abspath(__file__))
cpp_lib = ctypes.CDLL(os.path.join(module_path, 'propagator.so'))


# Propagator for individual aircraft
cpp_lib.propagate.argtypes = (ndpointer(dtype=ctypes.c_float, shape=(3,)),
                              ndpointer(dtype=ctypes.c_float, shape=(3,)),
                              ctypes.c_float, ctypes.c_float, ctypes.c_float,
                              ndpointer(dtype=ctypes.c_float, shape=(1,)))

# Propagator for simultaneous fleet propagation.
# TODO: remove shape, maybe replace with dim
cpp_lib.propagate_fleet.argtypes = (ndpointer(dtype=ctypes.c_float, shape=(-1, 3)),
                                    ndpointer(dtype=ctypes.c_float, shape=(-1, 3)),
                                    ctypes.c_float,
                                    ndpointer(dtype=ctypes.c_float, shape=(-1,)),
                                    ndpointer(dtype=ctypes.c_float, shape=(-1,)),
                                    ndpointer(dtype=ctypes.c_float, shape=(-1, 1)),
                                    ctypes.c_int)


c_propagator = cpp_lib.propagate
c_fleet_propagator = cpp_lib.propagate_fleet


# CUDA
cuda_lib = ctypes.CDLL(os.path.join(module_path, 'propagator_cuda.so'))

cuda_lib.propagate_cuda.argtypes = (ndpointer(dtype=ctypes.c_float),
                                     ndpointer(dtype=ctypes.c_float),
                                     ctypes.c_float,
                                     ndpointer(dtype=ctypes.c_float),
                                     ndpointer(dtype=ctypes.c_float),
                                     ndpointer(dtype=ctypes.c_float),
                                     ctypes.c_int)


cuda_propagator = cuda_lib.propagate_cuda

def get_fleet_propagator(N):

    """ Shape has to be set for the function. """
    # TODO: Check replacing shape kwarg with dim, avoiding having to set shape. At runtime N is passed anyways.  --> will make this unnecessary

    cpp_lib.propagate_fleet.argtypes = (ndpointer(dtype=ctypes.c_float, shape=(N, 3), ),
                                        ndpointer(dtype=ctypes.c_float, shape=(N, 3)),
                                        ctypes.c_float,
                                        ndpointer(dtype=ctypes.c_float, shape=(N, 1)),
                                        ndpointer(dtype=ctypes.c_float, shape=(N, 1)),
                                        ndpointer(dtype=ctypes.c_float, shape=(N, 1)),
                                        ctypes.c_int)
    return cpp_lib.propagate_fleet


if __name__ == "__main__":
    pos = np.array([1000, 5000, 300], dtype=np.float32)
    vel = np.array([100, 100, 0], dtype=np.float32)

    dt = float(1.0)
    turn_rate = float(45)
    climb_rate = float(55.0)

    print(pos, vel)

    cpp_lib.propagate(pos, vel, dt, turn_rate, climb_rate)

    print(pos, vel)
