import context
import json
import numpy as np
import utils.random_generator as random_generator
from typing import Final
from utils import task_json_io

def get_first_n_agents_from_task(n, a, s, t):
    a_n = a[:n]
    s_n = dict()
    t_n = dict()
    print(a_n, s_n, t_n)
    for i in a_n:
        s_n[i] = s[i]
        t_n[i] = t[i]
    print(len(a_n), len(s_n), len(t_n))
    return a_n, s_n, t_n


def generate_random_task(min_dist = 0.5, min_x = -5, max_x = 5, min_y = -5, max_y = 5, vert_num = 16, neighbours_max_num = 5, agents_num = 14):
    positions, all_neighbours = random_generator.generate_random_graph(min_dist, min_x, max_x, min_y, max_y, vert_num, neighbours_max_num)
    a, s, t = random_generator.generate_random_agents( agents_num, vert_num)
    return positions, all_neighbours, a, s, t


def main():
    min_dist: Final = 0.7
    min_x: Final = -5
    max_x: Final = 5
    min_y: Final = -5
    max_y: Final = 5
    vert_num: Final = 16
    neighbours_max_num: Final = 5
    max_agents_num: Final = 14
    min_agents_num = 5
    step_agents_num = 1
    ag_size: Final = 0.3
    task_num = 20
    task_dir = "../tasks/"

    for i in range(task_num):
        positions, all_neighbours, a, s, t = generate_random_task(min_dist, min_x, max_x, min_y, max_y, vert_num, neighbours_max_num, max_agents_num)
        for n in range(min_agents_num, max_agents_num+1, step_agents_num):
            a_n, s_n, t_n = get_first_n_agents_from_task(n, a, s, t)
            task_json_io.save_task_to_json(task_dir + str(n) + '_' + str(i) +"_task.json", positions, all_neighbours, a_n, s_n, t_n, ag_size)


if __name__ == "__main__":
    main()

