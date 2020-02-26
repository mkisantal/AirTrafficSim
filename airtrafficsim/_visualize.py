from matplotlib import pyplot as plt
from scipy import ndimage
import numpy as np
import os
from . import MODULE_PATH

LIM = 25000
ICON_SIZE = 1500
LABEL_OFFSET = 50
ICON_ROTATION_OFFSET = 60
ICON_OFFSET = -ICON_SIZE/20

#
# print(os.path.join(MODULE_PATH, '/stuff/aircraft_icon.png'))
# print(os.path.exists(os.path.join(MODULE_PATH, 'stuff/aircraft_icon.png')))
# print('--'*5)


ac_icon = plt.imread(os.path.join(MODULE_PATH, 'stuff/aircraft_icon.png'))


def center_icon(pos):
    left = pos[1] - ICON_SIZE/2 + ICON_OFFSET
    right = pos[1] + ICON_SIZE/2 + ICON_OFFSET
    bottom = pos[0] - ICON_SIZE/2 + ICON_OFFSET
    top = pos[0] + ICON_SIZE/2 + ICON_OFFSET

    return left, right, bottom, top


def plot_aircraft(jets, trails=True):
    if not (type(jets) is list) and not (type(jets) is tuple):
        jets = [jets]
    fig, ax = plt.subplots()

    ax.set_xlim([-LIM, LIM])
    ax.set_ylim([-LIM, LIM])
    ax.grid(True)
    for jet in jets:
        rotated_ac_icon = ndimage.rotate(ac_icon, -(jet.heading + ICON_ROTATION_OFFSET))  # negative as rot dir opposite
        ax.imshow(rotated_ac_icon, extent=center_icon(jet.position))
        t = ax.text(jet.position[1] + LABEL_OFFSET, jet.position[0] + LABEL_OFFSET,
                    jet.id)
        t.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='black'))

        if trails:
            ax.plot(jet.track[:, 1], jet.track[:, 0], 'k--')

    plt.show()
