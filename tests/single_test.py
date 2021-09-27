# TODO reading tasks_14_16 from JSON files

from context import pebble_search
from pebble_search.push_and_rotate import PushAndRotate
from pebble_search.size_push_and_rotate import PushAndRotateWithSizes
from pebble_search.graph import Graph as Graph
import utils.random_generator as random_generator
import utils.visualizer as visualizer
from utils import is_valid_solution
from utils import task_json_io

import numpy as np
import copy
import traceback
import sys

positions, all_neighbours, a, s, t, r = task_json_io.read_task_from_json("../tasks_10_16/2_task.json")

g = Graph(positions, all_neighbours)
solution = None
valid = False
success = False

solver = PushAndRotateWithSizes(g, a, s, t, r)
success, solution = solver.solve()
print("solve end")
if solution is not None:
    valid = is_valid_solution(g, a, s, t, solution)
print("Success:", success, "; Valid: ", valid)
if not valid or not success:
    random_generator.print_graph(positions, all_neighbours)
    print(a, s, t)

visualizer.draw(g, s, solution)


