import numpy as np


class solution:
    def __init__(self, decnum, objnum):
        self.dv = np.empty(decnum, np.float64)
        self.f = np.empty(objnum, np.float64)
        self.z = 0.0

        self.raw = 0.0
        self.density = 0.0
        self.fitness = 0.0
        self.lifetime = 1

        self.aux = 0.0
        self.psi = 0.0


def dominion_status(x1, x2):
    obj_val_precision = 7
    # non-domination
    ds = 0

    # x1 dominates x2
    if all(round(x, obj_val_precision) <= round(y, obj_val_precision) for x, y in zip(x1.f, x2.f)):
        ds = 1

    # x2 dominates x1
    elif all(round(x, obj_val_precision) <= round(y, obj_val_precision) for x, y in zip(x2.f, x1.f)):
        ds = 2
    return ds


def Update_Archive(archive, candidate):
    list_of_items_to_be_removed = []
    dominance_flag = 0
    for i in range(0, len(archive)):
        dominion_status_result = dominion_status(candidate, archive[i])
        if (dominion_status_result == 2):  # //candidate is dominated
            dominance_flag = -1
            return archive, dominance_flag
        elif dominion_status_result == 1:
            list_of_items_to_be_removed.append(i)

    archive = [i for j, i in enumerate(archive) if j not in list_of_items_to_be_removed]
    archive.append(candidate)
    return archive, dominance_flag






