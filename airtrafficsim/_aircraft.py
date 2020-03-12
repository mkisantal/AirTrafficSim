import numpy as np
from math import sin, cos, degrees, radians, atan2
from . import FLIGHT_LEVEL_TO_METER, FT_PER_MIN_TO_M_PER_SEC, c_propagator, BACKEND
import ctypes


class Fleet:

    """ Storing all Aircraft states in shared ndarrays. """

    def __init__(self, aircraft_list):

        self.ids = [ac.id for ac in aircraft_list]

        self.positions = np.stack([ac.position for ac in aircraft_list])
        self.velocities = np.stack([ac.velocity for ac in aircraft_list])
        self.headings = np.stack([ac.heading for ac in aircraft_list])
        self.turn_rates = np.stack([ac.turn_rate for ac in aircraft_list])
        self.climb_rates = np.stack([ac.climb_rate for ac in aircraft_list])

        self.tracks = [self.positions.copy()]

        # replacing original member variables with references to fleet values
        # bit ugly, but works
        # todo: what does it do to the C++ backend??
        for i, ac in enumerate(aircraft_list):
            ac.fleet = self
            ac.position = self.positions[i]
            ac.velocity = self.velocities[i]
            ac.heading = self.headings[i]
            ac.turn_rate = self.turn_rates[i]
            ac.climb_rate = self.climb_rates[i]

    def check(self):
        print(self.positions.shape)
        print(self.velocities.shape)
        print(self.headings.shape)
        print(self.turn_rates.shape)
        print(self.climb_rates.shape)

    def step(self, dt):
        # if len(self.tracks) == 0:
        #     self.tracks.append(self.positions.copy())

        self.velocities[:, 2] = self.climb_rates * FT_PER_MIN_TO_M_PER_SEC
        rotations = self.turn_rates[:, 0] * dt

        self.headings += rotations
        horizontal_speeds = np.linalg.norm(self.velocities[:, :2], axis=1)
        self.velocities[:, 0] = np.cos(self.headings) * horizontal_speeds
        self.velocities[:, 1] = np.sin(self.headings) * horizontal_speeds

        self.positions += self.velocities * dt
        self.tracks.append(self.positions.copy())


class Aircraft:

    """ Aircraft with state and basic kinematics. """

    def __init__(self, ac_id, start_pos=np.zeros(3), start_vel=np.array([200, 0, 0])):
        self.id = ac_id
        self.fleet = None

        # STATE
        self.position = np.float32(start_pos)  # meters
        self.velocity = np.float32(start_vel)  # meter/sec
        self.climb_rate = 0.0
        # needed to edd an extra dimension, otherwise not possible to establish reference with fleet
        self.turn_rate = np.float32([0.0])  # degrees/sec
        if BACKEND == 'C++':
            self.heading = ctypes.c_float(atan2(start_vel[1], start_vel[0]))
            self.step = self.step_cpp
        else:
            self.heading = float(atan2(start_vel[1], start_vel[0]))
            self.step = self.step_python
        self.speed = np.linalg.norm(start_vel)

        self.track = np.vstack([self.position.copy()])

    def step_python(self, dt):

        """ Propagate Aircraft state in python. """

        self.velocity[2] += self.climb_rate * FT_PER_MIN_TO_M_PER_SEC
        rotation = self.turn_rate * dt
        self.heading += radians(rotation)
        horizontal_speed = np.linalg.norm(self.velocity[:2])
        self.velocity[0] = cos(self.heading) * horizontal_speed
        self.velocity[1] = sin(self.heading) * horizontal_speed
        self.position += self.velocity * dt
        self.heading = atan2(self.velocity[1], self.velocity[0])

        self.track = np.vstack([self.track, self.position.copy()])

        if self.fleet is not None:
            self.fleet.tracks.append(self.fleet.positions.copy())

    def step_cpp(self, dt):

        """ Propagate Aircraft state with external C++ library. """

        c_propagator(self.position, self.velocity, float(dt),
                     float(self.turn_rate), float(self.climb_rate), ctypes.byref(self.heading))

        self.track = np.vstack([self.track, self.position.copy()])

    def step_CUDA(self, dt):

        """ Propagate Aircraft state with computation on GPU. """

        # TODO: implement this.
        raise NotImplementedError
