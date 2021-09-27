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


def single_test(min_dist = 0.5, min_x = -5, max_x = 5, min_y = -5, max_y = 5, vert_num = 16, neighbours_max_num = 5, agents_num = 14, vis = False):


    positions, all_neighbours = random_generator.generate_random_graph(min_dist, min_x, max_x, min_y, max_y, vert_num, neighbours_max_num)
    g = Graph(positions, all_neighbours)

    a, s, t = random_generator.generate_random_agents(vert_num=vert_num, agents_num=agents_num)


    solution = None
    try:
        solver = PushAndRotateWithSizes(g, a, s, t, 0.3)
        success, solution = solver.solve()
        valid = is_valid_solution(g,a,s,t,solution)
        print("Success:", success, "; Valid: ", valid)
        if not valid or not success:
            random_generator.print_graph(positions, all_neighbours)
            print(a, s, t)
            return False
    except Exception:
        print("Error")
        print(traceback.format_exc())
        random_generator.print_graph(positions, all_neighbours)
        print("a = ", a, "\ns = ", s, "\nt = ", t)
        return False
    
    if vis:
        visualizer.draw(g, s, solution)
    
    return True

   
single_test(min_dist = 0.5, min_x = -5, max_x = 5, min_y = -5, max_y = 4, vert_num = 10, neighbours_max_num = 5, agents_num = 5, vis = True)
