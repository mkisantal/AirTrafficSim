import airtrafficsim as ats
from random import random, randint


if __name__ == "__main__":

    jets = [ats.Aircraft(ac_id=ats.random_id(),
                         start_pos=ats.random_position(),
                         start_vel=ats.random_velocity(heading=None)) for i in range(7)]

    for i in range(400):

        ats.plot_aircraft(jets, out_path='./output')
        if i % 25 == 0:
            print(i)
        for jet in jets:
            jet.step(.2)
            if random() < 0.10:
                jet.heading += randint(-20, 20)

    print(jets[0].heading)

    print('Minden fasza.')