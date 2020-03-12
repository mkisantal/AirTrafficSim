import numpy as np
from math import sin, cos, degrees, radians, atan2
from . import FLIGHT_LEVEL_TO_METER, FT_PER_MIN_TO_M_PER_SEC, c_propagator, BACKEND
import ctypes


class Fleet:

    """ Storing all Aircraft states in shared ndarrays. """

    def __init__(self):
        self.aircraft = []
        self.positions = np.zeros([0, 3], dtype=np.float32)
        self.velocities = np.zeros([0, 3], dtype=np.float32)
        self.headings = np.zeros([0], dtype=np.float32)
        self.turn_rates = np.zeros([0], dtype=np.float32)
        self.climb_rates = np.zeros([0], dtype=np.float32)
        self.tracks = []
        self.tracks_np = None

    def get_track(self, i):
        if len(self.tracks) == 0:
            raise ValueError('No tracks yet.')
        if self.tracks_np is None or len(self.tracks) > self.tracks_np.shape[0]:
            self.tracks_np = np.stack(self.tracks)

        return self.tracks_np[:, i, :]

    def step(self, dt):
        if len(self.tracks) == 0:
            self.tracks.append(self.positions.copy())

        self.velocities[:, 2] = self.climb_rates
        rotations = self.turn_rates * dt

        self.headings += rotations
        horizontal_speeds = np.linalg.norm(self.velocities[:, :2], axis=1)
        self.velocities[:, 0] = np.cos(self.headings) * horizontal_speeds
        self.velocities[:, 1] = np.sin(self.headings) * horizontal_speeds

        self.positions += self.velocities * dt
        self.tracks.append(self.positions.copy())


fleet = Fleet()


class Aircraft:

    """ Aircraft with state and basic kinematics. """

    def __init__(self, ac_id, start_pos=np.zeros(3), start_vel=np.array([200, 0, 0])):
        self.id = ac_id
        fleet.aircraft.append(self)

        # STATE
        self.i = fleet.positions.shape[0]
        fleet.positions = np.append(fleet.positions, np.expand_dims(np.float32(start_pos), 0), axis=0)
        fleet.velocities = np.append(fleet.velocities, np.expand_dims(np.float32(start_vel), 0), axis=0)
        fleet.turn_rates = np.append(fleet.turn_rates, np.zeros([1]))
        fleet.climb_rates = np.append(fleet.climb_rates, np.zeros([1]))

        self.position = fleet.positions[self.i]  # meters
        self.velocity = fleet.velocities[self.i]  # meter/sec
        self.climb_rate = fleet.climb_rates[self.i]
        self.turn_rate = fleet.turn_rates[self.i]  # degrees/sec
        if BACKEND == 'C++':
            self.heading = ctypes.c_float(atan2(start_vel[1], start_vel[0]))
            self.step = self.step_cpp
        else:
            fleet.headings = np.append(fleet.headings, np.float32([[atan2(start_vel[1], start_vel[0])]]))
            self.heading = fleet.headings[self.i]
            self.step = self.step_python
        self.speed = np.linalg.norm(start_vel)

        self.track = np.vstack([self.position.copy()])

    def get_track(self):
        if len(fleet.tracks) > self.track.shape[0]:
            return fleet.get_track(self.i)
        else:
            return self.track

    def get_position(self):
        if len(fleet.tracks) > self.track.shape[0]:
            return fleet.positions[self.i]
        else:
            return self.position

    def get_heading(self):
        if len(fleet.tracks) > self.track.shape[0]:
            return fleet.headings[self.i]
        else:
            return self.heading

    def set_turn_rate(self, turn_rate):
        fleet.turn_rates[self.i] += turn_rate

    def step_python(self, dt):

        """ Propagate Aircraft state in python. """

        self.velocity[2] = self.climb_rate * FT_PER_MIN_TO_M_PER_SEC
        rotation = self.turn_rate * dt
        self.heading += radians(rotation)
        horizontal_speed = np.linalg.norm(self.velocity[:2])
        self.velocity[0] = cos(self.heading) * horizontal_speed
        self.velocity[1] = sin(self.heading) * horizontal_speed
        self.position += self.velocity * dt
        # self.heading = atan2(self.velocity[1], self.velocity[0])

        self.track = np.vstack([self.track, self.position.copy()])

    def step_cpp(self, dt):

        """ Propagate Aircraft state with external C++ library. """

        c_propagator(self.position, self.velocity, float(dt),
                     float(self.turn_rate), float(self.climb_rate), ctypes.byref(self.heading))

        self.track = np.vstack([self.track, self.position.copy()])

    def step_CUDA(self, dt):

        """ Propagate Aircraft state with computation on GPU. """

        # TODO: implement this.
        raise NotImplementedError
