
from context import pebble_search
from pebble_search.push_and_rotate import PushAndRotate as PushAndRotate
from pebble_search.graph import Graph as Graph
import utils.random_generator as random_generator
import utils.visualizer as visualizer


import numpy as np
import copy
import traceback
import sys

def is_valid_solution(graph, agents, starts, goals, solution):
    if solution is None:
        print("Solution not found")

    agents_positions = copy.deepcopy(starts)
    reached_goals = set() 
    empty_vertices = copy.deepcopy(graph.vertices)
    occupied_vertices = dict()

    for agent, vert in starts.items():
        occupied_vertices.update({vert : agent})
        empty_vertices.remove(vert)
    
    step = 0
    for agent, v_from, v_to in solution:
        step += 1
        # print(step)
        # print("\t(move) Agent:", agent, "from", v_from, "to", v_to)
        if agents_positions[agent] != v_from:
            print("Error: move from incorrect position!", agent, v_from, v_to)
            return False
        if v_to in occupied_vertices:
            print("Error: move to occupied position!", agent, v_from, v_to)
            return False
        if v_to not in graph.get_neighbours(v_from):
            print("Error: move to vertex withou edge!", agent, v_from, v_to)
            return False

        empty_vertices.add(v_from)
        empty_vertices.remove(v_to)
        occupied_vertices.update({v_to : agent})
        occupied_vertices.pop(v_from)
        agents_positions[agent] = v_to


    for agent, pos in agents_positions.items():
        if pos != goals[agent]:
            print("Agent", agent, "doesnt reach goal")
            return False
    return True

def single_test(min_dist = 0.5, min_x = -5, max_x = 5, min_y = -5, max_y = 5, vert_num = 30, neighbours_max_num = 5, agents_num = 20, vis = False):
    
    positions, all_neighbours = random_generator.generate_random_graph(min_dist, min_x, max_x, min_y, max_y, vert_num, neighbours_max_num)
    g = Graph()

    for i in range(vert_num):
        g.add_vertex( i , positions[i], all_neighbours[i])

    a, s, t = random_generator.generate_random_agents(vert_num=vert_num, agents_num=agents_num)
    solution = None
    try:
        solver = PushAndRotate(g, a, s, t)
        success, solution = solver.solve()
        valid = is_valid_solution(g,a,s,t,solution)
        print("Success:", success, "; Valid: ", valid)
        if not valid or not success:
            random_generator.print_graph(vert_num, positions, all_neighbours)
            print(a, s, t)
            return False
    except Exception:
        print("Error")
        print(traceback.format_exc())
        random_generator.print_graph(vert_num, positions, all_neighbours)
        print("a = ", a, "\ns = ", s, "\nt = ", t)
        return False
    
    if vis:
        visualizer.draw(g, s, solution)
    
    return True

for i in range(1):         
    if not single_test(min_dist = 0.5, min_x = -5, max_x = 5, min_y = -5, max_y = 4, vert_num = 50, neighbours_max_num = 5, agents_num = 45, vis = False):
        exit(-1)