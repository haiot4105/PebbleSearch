import visualizer
from graph import Graph
from push_and_swap import PushAndSwap
import numpy as np
import copy
import random_generator

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





# positions, all_neighbours = random_generator.generate_random_graph(min_dist, min_x , max_x, min_y , max_y, vert_num , neighbours_max_num )
g = Graph()
g.add_vertex( 0 , np.array([ -4.484706907438003 , 4.143077260708379 ]), { 19, 20, 6, 7 })
g.add_vertex( 1 , np.array([ -3.045206481960302 , -1.274916251283603 ]), { 25, 3, 4 })
g.add_vertex( 2 , np.array([ -0.25261828454632873 , 3.038115600596335 ]), { 5, 6, 15, 16, 23 })
g.add_vertex( 3 , np.array([ -3.1272968019703464 , 0.324167516187714 ]), { 1, 22, 6, 25 })
g.add_vertex( 4 , np.array([ -0.3244490078583251 , -3.184503195864191 ]), { 1, 29, 27, 12, 13 })
g.add_vertex( 5 , np.array([ -0.22543645252546174 , 4.85972603981312 ]), { 16, 2, 23, 28, 15 })
g.add_vertex( 6 , np.array([ -1.5372847921156874 , 2.1943585809432786 ]), { 0, 2, 3, 16, 22 })
g.add_vertex( 7 , np.array([ -3.4425610596689005 , 3.0524861073883933 ]), { 0, 19, 20, 22 })
g.add_vertex( 8 , np.array([ 3.023614645212307 , 3.066070717789522 ]), { 21, 23, 26, 28, 14 })
g.add_vertex( 9 , np.array([ -4.794045625554997 , -2.833206499660905 ]), { 25, 18, 11 })
g.add_vertex( 10 , np.array([ 3.863815654043499 , -1.5230294282338184 ]), { 17, 24, 26, 27, 29 })
g.add_vertex( 11 , np.array([ -4.509607402794248 , -4.195880926556078 ]), { 9, 18 })
g.add_vertex( 12 , np.array([ -2.534315787347756 , -3.5386154586144194 ]), { 18, 4, 13 })
g.add_vertex( 13 , np.array([ -2.7085384730458886 , -4.368336339448104 ]), { 18, 4, 25, 12 })
g.add_vertex( 14 , np.array([ 1.8087594847156776 , 2.0512042773637162 ]), { 8, 26, 23 })
g.add_vertex( 15 , np.array([ 0.2721394532037458 , 4.686211051622166 ]), { 2, 5 })
g.add_vertex( 16 , np.array([ -1.4839561547674784 , 3.7309692072061402 ]), { 2, 5, 6 })
g.add_vertex( 17 , np.array([ 3.414347104807792 , -2.9859481285746736 ]), { 24, 10, 27, 29 })
g.add_vertex( 18 , np.array([ -3.654873052179383 , -3.6855110648029346 ]), { 9, 11, 12, 13 })
g.add_vertex( 19 , np.array([ -4.247841063048169 , 4.747120479564309 ]), { 0, 20, 7 })
g.add_vertex( 20 , np.array([ -3.4252433009697625 , 4.288870104920747 ]), { 0, 19, 7 })
g.add_vertex( 21 , np.array([ 4.3648032380104524 , 2.786455412601523 ]), { 8, 26 })
g.add_vertex( 22 , np.array([ -2.1816809159841277 , 1.4460715949279122 ]), { 3, 6, 7 })
g.add_vertex( 23 , np.array([ 0.77932487499882 , 2.068984329633058 ]), { 8, 2, 5, 14 })
g.add_vertex( 24 , np.array([ 4.908278968019301 , -2.8721262511075296 ]), { 17, 10, 27 })
g.add_vertex( 25 , np.array([ -3.633967827386635 , -2.1285910024062735 ]), { 1, 3, 13, 9 })
g.add_vertex( 26 , np.array([ 3.331436152501116 , 1.0843128087992016 ]), { 21, 8, 10, 14 })
g.add_vertex( 27 , np.array([ 1.508850902019212 , -1.2780570669232096 ]), { 24, 17, 10, 4 })
g.add_vertex( 28 , np.array([ 2.634492367711778 , 4.336673460920874 ]), { 8, 5 })
g.add_vertex( 29 , np.array([ -0.06037857943481573 , -2.446046010905526 ]), { 17, 10, 4 })
a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] 
s = {0: 21, 1: 25, 2: 28, 3: 18, 4: 16, 5: 5, 6: 8, 7: 24, 8: 9, 9: 2, 10: 11, 11: 19, 12: 12, 13: 29, 14: 15, 15: 10, 16: 22, 17: 0, 18: 1, 19: 3} 
t = {0: 15, 1: 13, 2: 0, 3: 25, 4: 26, 5: 19, 6: 23, 7: 22, 8: 10, 9: 7, 10: 5, 11: 6, 12: 16, 13: 2, 14: 1, 15: 8, 16: 9, 17: 24, 18: 20, 19: 28}
solution = None

solver = PushAndSwap(g, a, s, t)
success, solution = solver.solve()
valid = is_valid_solution(g,a,s,t,solution)
print("Success:", success, "; Valid: ", valid)
if not valid or not success:
    random_generator.print_graph(vert_num, positions, all_neighbours)
    print(a, s, t)

visualizer.draw(g, s, solution)


