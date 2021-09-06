# TODO reading tasks from JSON files

from context import pebble_search
from pebble_search.push_and_rotate import PushAndRotate
from pebble_search.size_push_and_rotate import PushAndRotateWithSizes
from pebble_search.graph import Graph as Graph
import utils.random_generator as random_generator
import utils.visualizer as visualizer
from utils import is_valid_solution

import numpy as np
import copy
import traceback
import sys

# positions = {0: np.array([2.5, 1.5]),
#              1: np.array([1.5, 2.5]),
#              2: np.array([2.5, 2.5]),
#              3: np.array([1.5, 4.5]),
#              4: np.array([4.5, 1.5]),
#              5: np.array([4.5, 3.5])}
#
# all_neighbours = {0: {3, 4},
#                   1: {2, 3, 4},
#                   2: {1, 3, 4},
#                   3: {0, 1, 2, 5},
#                   4: {2, 0, 5, 1},
#                   5: {3, 4}}
#
# g = Graph(positions, all_neighbours)
# a = [0, 1, 2]
# r = [0.4 for _ in range(5)]
# s = {0: 0, 1: 1, 2: 2}
# t = {0: 3, 1: 1, 2: 2}

positions = {0: np.array([2.5, 1.5]),
             1: np.array([1.5, 3.5]),
             2: np.array([1.5, 5.5]),
             3: np.array([4.5, 0.5]),
             4: np.array([3.5, 0.5]),
             5: np.array([0.5, 4.5])}

all_neighbours = {0: {2, 5, 4},
                  1: {3, 4},
                  2: {0, 3, 4, 5},
                  3: {1, 2, 4},
                  4: {1, 2, 3, 0},
                  5: {0, 2}}

g = Graph(positions, all_neighbours)
a = [0, 1]
r = [0.4 for _ in range(2)]
s = {0: 0, 1: 1}
t = {0: 2, 1: 1}

solution = None

solver = PushAndRotateWithSizes(g, a, s, t, r)
success, solution = solver.solve()
valid = is_valid_solution(g, a,s,t,solution)
print("Success:", success, "; Valid: ", valid)
if not valid or not success:
    random_generator.print_graph(positions, all_neighbours)
    print(a, s, t)

visualizer.draw(g, s, solution)


