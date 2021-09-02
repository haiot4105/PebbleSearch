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

positions = {0: np.array([-4.40510342, -2.49121872]), 1: np.array([-2.33350004,  4.6258613 ]), 2: np.array([ 4.19330149, -3.80902373]), 3: np.array([1.54975851, 1.07695815]), 4: np.array([-2.03891739, -2.10929181]), 5: np.array([ 4.26565985, -0.47874631]), 6: np.array([-0.47442438,  3.32796739]), 7: np.array([3.08541033, 1.38806081]), 8: np.array([ 3.2159008 , -4.32690637]), 9: np.array([-1.45743893,  0.31132419])}

all_neighbours = {0: {1, 3, 4, 8, 9}, 4: {0, 9}, 9: {0, 3, 4, 6}, 3: {0, 1, 2, 5, 7, 9}, 1: {0, 3, 6, 7}, 8: {0, 2, 5}, 6: {1, 9}, 7: {1, 3, 5}, 2: {8, 3, 5}, 5: {2, 3, 7, 8}}
g = Graph(positions, all_neighbours)
a = [0, 1, 2, 3, 4]
r = [0.3 for _ in range(5)]
s = {0: 5, 1: 2, 2: 4, 3: 6, 4: 7}
t = {0: 3, 1: 7, 2: 2, 3: 8, 4: 1}

solution = None

solver = PushAndRotateWithSizes(g, a, s, t, r)
success, solution = solver.solve()
valid = is_valid_solution(g,a,s,t,solution)
print("Success:", success, "; Valid: ", valid)
if not valid or not success:
    random_generator.print_graph(positions, all_neighbours)
    print(a, s, t)

visualizer.draw(g, s, solution)


