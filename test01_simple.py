import airtrafficsim as ats
from random import random, randint, choice
import time
from math import radians


if __name__ == "__main__":

    jets = [ats.Aircraft(ac_id=ats.random_id(),
                         start_pos=ats.random_position(),
                         start_vel=ats.random_velocity(heading=None)) for i in range(10)]

    t0 = time.time()

    fleet = ats.Fleet(jets)
    fleet.check()

    for i in range(10):
        jets[0].step(1.0)
        # ats.plot_aircraft(jets, out_path='./output')
        ats.plot_fleet(fleet, out_path='./output')
        # print(jets[0].position)

    for i in range(20):
        fleet.step(1.0)
        ac = choice(jets)
        ac.turn_rate += radians(5)
        ats.plot_fleet(fleet, out_path='./output')

    t1 = time.time()
    print(t1-t0)

    print(jets[0].heading)

    print('Minden fasza.')