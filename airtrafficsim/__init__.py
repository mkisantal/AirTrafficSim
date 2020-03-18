import numpy as np
import os
from math import radians

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

FT_PER_MIN_TO_M_PER_SEC = 0.00508
FLIGHT_LEVEL_TO_METER = 30.48
STANDARD_TURN_RATE = radians(3)

BACKEND = None  # None, C++, CUDA
PARALLEL = True
DEBUG = False

from ._propagator import c_propagator, get_fleet_propagator, cuda_propagator
from ._aircraft import Aircraft, Fleet
from ._visualize import plot_aircraft, plot_fleet
from ._utils import random_position, random_velocity, random_id
