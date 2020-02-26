from random import randint, choice
from math import cos, sin, radians
import numpy as np


def random_position(xlims=[-10000, 10000], ylims=[-10000, 10000], zlims=[-12000, -5000]):

    return np.array([randint(*xlims), randint(*ylims), randint(*zlims)])


def random_velocity(speed_lims=[250, 350], heading=None):
    random_hdg = radians(randint(0, 72) * 5 if heading is None else heading)
    random_speed = randint(*speed_lims)
    return np.array([cos(random_hdg)*random_speed, sin(random_hdg)*random_speed, 0])


def random_id():
    letters = list('ABCDEFGHJKLMNOPQRSTV')
    airlines = ['RYR', 'WZZ', 'DLH', 'AUA', 'EZY', 'THY']
    return choice(airlines) + (str(randint(10, 150)) + choice(letters) + choice(letters))[:4]
