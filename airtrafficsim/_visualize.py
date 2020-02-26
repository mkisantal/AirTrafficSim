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


ac_icon = np.uint8(plt.imread(os.path.join(MODULE_PATH, 'stuff/aircraft_icon.png'))*255.0)

FRAME_COUNTER = 0


def center_icon(pos):
    left = pos[1] - ICON_SIZE/2 + ICON_OFFSET
    right = pos[1] + ICON_SIZE/2 + ICON_OFFSET
    bottom = pos[0] - ICON_SIZE/2 + ICON_OFFSET
    top = pos[0] + ICON_SIZE/2 + ICON_OFFSET

    return left, right, bottom, top


def plot_aircraft(jets, trails=True, out_path=None):
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

    if out_path is None:
        plt.show()
    else:
        global FRAME_COUNTER
        fig.savefig(os.path.join(out_path, 'frame_{:05d}'.format(FRAME_COUNTER)))
        FRAME_COUNTER += 1
        plt.close(fig)
