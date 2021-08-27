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
g.add_vertex( 0 , np.array([ 4.307713779737119 , 0.9864085482553211 ]), { 24, 9, 5, 15 })
g.add_vertex( 1 , np.array([ 0.6126579639266208 , 3.788217891106102 ]), { 29, 27, 5, 7 })
g.add_vertex( 2 , np.array([ -0.03710076048105293 , -3.4919085165152963 ]), { 26, 18, 12, 4 })
g.add_vertex( 3 , np.array([ 4.256625642141703 , -3.092711141619162 ]), { 8, 10, 21 })
g.add_vertex( 4 , np.array([ -1.2664838134526102 , -4.3758200564136125 ]), { 11, 18, 2, 20 })
g.add_vertex( 5 , np.array([ 1.3167570733379188 , 2.506397606360215 ]), { 0, 1, 17, 7, 9, 27, 29 })
g.add_vertex( 6 , np.array([ -3.3835152695848425 , -1.384075821817082 ]), { 19, 11, 23 })
g.add_vertex( 7 , np.array([ 0.40458667991941866 , 4.2703072001213584 ]), { 1, 5 })
g.add_vertex( 8 , np.array([ 4.696674911159192 , -3.6231610040233218 ]), { 10, 3, 21 })
g.add_vertex( 9 , np.array([ 4.62747840246311 , 1.9654238904983803 ]), { 0, 17, 5, 24 })
g.add_vertex( 10 , np.array([ 3.190247366975129 , -2.37600275369944 ]), { 8, 3, 28, 15 })
g.add_vertex( 11 , np.array([ -1.8354852638933492 , -2.6743228492349216 ]), { 4, 20, 6, 23 })
g.add_vertex( 12 , np.array([ 0.8422393654212765 , -4.03920002912886 ]), { 16, 2, 26 })
g.add_vertex( 13 , np.array([ -1.1145030846892268 , 1.4907568224881382 ]), { 25, 27, 29, 22 })
g.add_vertex( 14 , np.array([ -3.6870356149500094 , 3.869671894663565 ]), { 19, 22 })
g.add_vertex( 15 , np.array([ 1.624740459597506 , -0.9274357516781215 ]), { 0, 25, 10, 28 })
g.add_vertex( 16 , np.array([ 1.532119388563559 , -3.669271541533262 ]), { 12, 28 })
g.add_vertex( 17 , np.array([ 4.201740695815472 , 4.5405393822712945 ]), { 24, 9, 5 })
g.add_vertex( 18 , np.array([ -0.9585233185587505 , -3.5406238767926523 ]), { 2, 26, 4, 20 })
g.add_vertex( 19 , np.array([ -4.949270584540426 , 0.8708369910351408 ]), { 6, 14 })
g.add_vertex( 20 , np.array([ -3.0690991464222392 , -4.863008003201529 ]), { 18, 11, 4, 23 })
g.add_vertex( 21 , np.array([ 3.7711553903249033 , -3.4789136416238433 ]), { 8, 3, 28 })
g.add_vertex( 22 , np.array([ -1.9721220410694897 , 2.971829582898895 ]), { 13, 14 })
g.add_vertex( 23 , np.array([ -3.35586828079368 , -3.1030934220547355 ]), { 20, 6, 11 })
g.add_vertex( 24 , np.array([ 4.466242302321842 , 3.813005412241239 ]), { 0, 17, 9 })
g.add_vertex( 25 , np.array([ 0.5725325888912947 , 0.48095977414619107 ]), { 29, 13, 15 })
g.add_vertex( 26 , np.array([ 0.2414658829621974 , -2.74673275560261 ]), { 2, 18, 12 })
g.add_vertex( 27 , np.array([ -0.10598199107808437 , 2.3408681114736094 ]), { 1, 13, 5 })
g.add_vertex( 28 , np.array([ 2.334372536687159 , -2.689106905271327 ]), { 16, 21, 10, 15 })
g.add_vertex( 29 , np.array([ 0.3745366060470392 , 2.1109968551440614 ]), { 1, 13, 5, 25 })
a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
s = {0: 18, 1: 17, 2: 21, 3: 15, 4: 2, 5: 4, 6: 13, 7: 27, 8: 6, 9: 25, 10: 23, 11: 8, 12: 19, 13: 9, 14: 11, 15: 20, 16: 16, 17: 24, 18: 10, 19: 29} 
t = {0: 2, 1: 24, 2: 13, 3: 26, 4: 8, 5: 6, 6: 25, 7: 17, 8: 15, 9: 29, 10: 21, 11: 10, 12: 27, 13: 28, 14: 18, 15: 3, 16: 0, 17: 14, 18: 4, 19: 7}
solution = None

solver = PushAndSwap(g, a, s, t)
success, solution = solver.solve()
valid = is_valid_solution(g,a,s,t,solution)
print("Success:", success, "; Valid: ", valid)
if not valid or not success:
    random_generator.print_graph(vert_num, positions, all_neighbours)
    print(a, s, t)

visualizer.draw(g, s, solution)


