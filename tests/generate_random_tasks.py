import context
import json
import numpy as np
import utils.random_generator as random_generator
from typing import Final
from utils import task_json_io

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
    agents_num: Final = 10
    ag_size: Final = 0.3
    task_num = 10
    task_dir = "../tasks_10_16/"

    for i in range(task_num):
        positions, all_neighbours, a, s, t = generate_random_task(min_dist, min_x, max_x, min_y, max_y, vert_num, neighbours_max_num, agents_num)
        task_json_io.save_task_to_json(task_dir + str(i) + "_task.json", positions, all_neighbours, a, s, t, ag_size)


if __name__ == "__main__":
    main()

