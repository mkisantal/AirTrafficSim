import numpy as np
from math import sin, cos, degrees, radians, atan2
from . import FLIGHT_LEVEL_TO_METER, FT_PER_MIN_TO_M_PER_SEC, c_propagator, get_fleet_propagator, BACKEND, DEBUG


class Fleet:

    """ Class for multiple planes. Vectorized propagation. """

    def __init__(self, aircraft_list):

        self.ids = [ac.id for ac in aircraft_list]

        self.positions = np.stack([ac.position for ac in aircraft_list])
        self.velocities = np.stack([ac.velocity for ac in aircraft_list])
        self.headings = np.stack([ac.heading for ac in aircraft_list])
        self.turn_rates = np.stack([ac.turn_rate for ac in aircraft_list])
        self.climb_rates = np.stack([ac.climb_rate for ac in aircraft_list])

        self.tracks = [self.positions.copy()]

        # Replacing original member variables with references to fleet values.
        # This allows both simultaneous and independent state updates.
        for i, ac in enumerate(aircraft_list):
            ac.fleet = self
            ac.position = self.positions[i]
            ac.velocity = self.velocities[i]
            ac.heading = self.headings[i]
            ac.turn_rate = self.turn_rates[i]
            ac.climb_rate = self.climb_rates[i]

        self.step = self.step_cpp if BACKEND=='C++' else self.step_python
        self._step_cpp = get_fleet_propagator(len(self.ids))

    def step_python(self, dt):

        """ Vectorized propagation with numpy.  """

        if DEBUG:
            print('normal fleet step')

        rotations = self.turn_rates[:, 0] * dt
        self.headings[:, 0] += np.radians(rotations)

        horizontal_speeds = np.linalg.norm(self.velocities[:, :2], axis=1)
        self.velocities[:, 0] = np.cos(self.headings[:, 0]) * horizontal_speeds
        self.velocities[:, 1] = np.sin(self.headings[:, 0]) * horizontal_speeds
        self.velocities[:, 2] = self.climb_rates[:, 0] * FT_PER_MIN_TO_M_PER_SEC

        self.positions += self.velocities * dt
        self.tracks.append(self.positions.copy())

    def step_cpp(self, dt):

        """ C++ propagation (for loop).  """

        if DEBUG:
            print('fleet C++ step')

        self._step_cpp(self.positions,
                       self.velocities,
                       float(dt),
                       self.turn_rates,
                       self.climb_rates,
                       self.headings,
                       int(len(self.ids)))  # We need to provide size information for cpp lib.

        self.tracks.append(self.positions.copy())


class Aircraft:

    """ Aircraft with state and basic kinematics. """

    def __init__(self, ac_id, start_pos=np.zeros(3), start_vel=np.array([200, 0, 0])):
        self.id = ac_id
        self.fleet = None

        # STATE
        self.position = np.float32(start_pos)  # meters
        self.velocity = np.float32(start_vel)  # meter/sec
        self.climb_rate = np.float32([0.0])
        # needed to edd an extra dimension, otherwise not possible to establish reference with fleet
        self.turn_rate = np.float32([0.0])  # degrees/sec
        if BACKEND == 'C++':
            self.heading = np.float32([atan2(start_vel[1], start_vel[0])])
            self.step = self.step_cpp
        else:
            self.heading = np.float32([atan2(start_vel[1], start_vel[0])])  # this may break link between ac and fleet
            self.step = self.step_python
        self.speed = np.linalg.norm(start_vel)

        self.track = np.vstack([self.position.copy()])

    def step_python(self, dt):

        """ Propagate Aircraft state in python. """

        if DEBUG:
            print('Python aircraft step')

        self.velocity[2] += self.climb_rate * FT_PER_MIN_TO_M_PER_SEC
        rotation = self.turn_rate * dt
        self.heading += radians(rotation)
        horizontal_speed = np.linalg.norm(self.velocity[:2])
        self.velocity[0] = cos(self.heading[0]) * horizontal_speed
        self.velocity[1] = sin(self.heading[0]) * horizontal_speed
        self.position += self.velocity * dt
        self.heading[0] = atan2(self.velocity[1], self.velocity[0])

        self.track = np.vstack([self.track, self.position.copy()])

        if self.fleet is not None:
            self.fleet.tracks.append(self.fleet.positions.copy())

    def step_cpp(self, dt):

        """ Propagate Aircraft state with external C++ library. """

        if DEBUG:
            print('C++ aircraft step')

        c_propagator(self.position, self.velocity, float(dt),
                     float(self.turn_rate), float(self.climb_rate), self.heading)

        self.track = np.vstack([self.track, self.position.copy()])

    def step_CUDA(self, dt):

        """ Propagate Aircraft state with computation on GPU. """

        # TODO: implement this.
        raise NotImplementedError
