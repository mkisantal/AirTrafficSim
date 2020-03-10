import numpy as np
from math import sin, cos, degrees, radians, atan2
from . import FLIGHT_LEVEL_TO_METER, FT_PER_MIN_TO_M_PER_SEC, c_propagator


class Aircraft:
    def __init__(self, ac_id, start_pos=np.zeros(3), start_vel=np.array([200, 0, 0])):
        self.id = ac_id

        # STATE
        self.position = np.float32(start_pos) # meters
        self.velocity = np.float32(start_vel)  # meter/sec
        self.climb_rate = 0
        self.turn_rate = 0  # degrees/sec
        self.heading = degrees(atan2(start_vel[1], start_vel[0]))
        self.speed = np.linalg.norm(start_vel)

        self.track = np.vstack([self.position.copy()])

    def step(self, dt):

        self.velocity[2] += self.climb_rate * FT_PER_MIN_TO_M_PER_SEC
        rotation = self.turn_rate * dt
        self.heading += rotation
        horizontal_speed = np.linalg.norm(self.velocity[:2])
        self.velocity[0] = cos(radians(self.heading)) * horizontal_speed
        self.velocity[1] = sin(radians(self.heading)) * horizontal_speed
        self.position += self.velocity * dt
        self.heading = degrees(atan2(self.velocity[1], self.velocity[0]))

        self.track = np.vstack([self.track, self.position.copy()])

    def step2(self, dt):
        c_propagator(self.position, self.velocity, float(dt),
                     float(self.turn_rate), float(self.climb_rate))

        self.track = np.vstack([self.track, self.position.copy()])
