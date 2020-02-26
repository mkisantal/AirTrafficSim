import airtrafficsim as ats
from random import random, randint, choice


if __name__ == "__main__":

    jets = [ats.Aircraft(ac_id=ats.random_id(),
                         start_pos=ats.random_position(),
                         start_vel=ats.random_velocity(heading=None)) for i in range(7)]

    for i in range(60):
        if i % 100 == 0:
            print(i)
        for jet in jets:
            jet.step(1)
            if random() < 0.15:
                jet.heading += randint(-20, 20)

    print(jets[0].heading)
    ats.plot_aircraft(jets)

    print('Minden fasza.')