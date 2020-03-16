import airtrafficsim as ats
from random import random, randint, choice
import time
from math import radians
import numpy as np


if __name__ == "__main__":

    print('Test started.')

    jets = [ats.Aircraft(ac_id=ats.random_id(),
                         start_pos=ats.random_position(),
                         start_vel=ats.random_velocity(heading=None)) for i in range(10)]

    t0 = time.time()

    fleet = ats.Fleet(jets)

    print('Aircraft and fleet are initialized. Running simulation...')

    if ats.PARALLEL:
        for i in range(20):
            fleet.step(5.0)
            ac = choice(jets)
            fleet.turn_rates += np.radians(np.random.randint(-90, 0, fleet.turn_rates.shape))
            ac.turn_rate += radians(5)
            ats.plot_fleet(fleet, out_path='./output')
    else:
        for i in range(20):
            for jet in jets:
                jet.step(4.0)
                jet.turn_rate += radians(randint(-90, 0))
            ats.plot_aircraft(jets, out_path='./output')


    t1 = time.time()
    print(t1-t0)
    print('Minden fasza.')