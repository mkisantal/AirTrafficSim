import airtrafficsim as ats
from random import random, randint
import time
from math import radians


if __name__ == "__main__":

    jets = [ats.Aircraft(ac_id=ats.random_id(),
                         start_pos=ats.random_position(),
                         start_vel=ats.random_velocity(heading=None)) for i in range(10)]

    t0 = time.time()

    for i in range(50):
        ats.plot_aircraft(jets, out_path='./output')
        if i % 25 == 0:

            print(i)

        ats._aircraft.fleet.step(1)
        for jet in jets:
            # jet.step(1)
            if random() < 0.1:
                jet.set_turn_rate(radians(randint(-1, 1)))

    t1 = time.time()
    print(t1-t0)

    print(jets[0].heading)

    print('Minden fasza.')