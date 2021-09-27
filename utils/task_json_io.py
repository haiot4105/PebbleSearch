import json
import numpy as np


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def save_task_to_json(file_name, positions, all_neighbours, a, s, t, size):
    fp = open(file_name, 'w')
    obj = {"graph": all_neighbours,
           "vert_positions": positions,
           "agents": a,
           "starts": s,
           "goals": t,
           "size": size}
    json.dump(obj, fp, indent=2,  cls=MyEncoder)


# def jsonKeys2int(x):
#     if 'graph' in x:
#         return x
#     if isinstance(x, dict):
#             return {int(k):v for k,v in x.items()}
#     return x

def read_task_from_json(file_name):
    fp = open(file_name, 'r')
    task_dict = json.load(fp)

    pos_str = task_dict["vert_positions"]
    positions = dict()
    for v_id, v_pos in pos_str.items():
        positions[int(v_id)] = np.array(v_pos)

    all_neighbours_str = task_dict["graph"]
    all_neighbours = dict()
    for v_id, v_n in all_neighbours_str.items():
        all_neighbours[int(v_id)] = set(v_n)

    agents = task_dict["agents"]

    starts_str = task_dict["starts"]
    starts = dict()
    for a_id, v_id in starts_str.items():
        starts[int(a_id)] = v_id

    goals_str = task_dict["goals"]
    goals = dict()
    for a_id, v_id in goals_str.items():
        goals[int(a_id)] = v_id

    size = task_dict["size"]

    return positions, all_neighbours, agents, starts, goals, size