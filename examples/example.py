# TODO make it works

import visualizer
from graph import Graph
from push_and_rotate import PushAndRotate
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
g.add_vertex( 0 , np.array([ -0.05284188962082936 , 3.2377989210794578 ]), { 33, 20, 38 })
g.add_vertex( 1 , np.array([ 3.7111446436802904 , -3.6875482804300317 ]), { 16, 17, 2, 21 })
g.add_vertex( 2 , np.array([ 4.902359504714301 , -4.709740163861828 ]), { 1, 17, 21, 44 })
g.add_vertex( 3 , np.array([ 4.906996912568269 , 1.7924076214549478 ]), { 32, 31 })
g.add_vertex( 4 , np.array([ -4.617244065087732 , -3.1019583029719695 ]), { 49, 40, 42, 11, 15 })
g.add_vertex( 5 , np.array([ 1.6991954336958397 , -3.328096856919788 ]), { 16, 8, 19, 29 })
g.add_vertex( 6 , np.array([ -3.54973195610535 , 2.09729704745547 ]), { 24, 10, 12, 46 })
g.add_vertex( 7 , np.array([ 0.743820113205695 , 1.854308070622733 ]), { 33, 36, 41, 20, 22 })
g.add_vertex( 8 , np.array([ 1.0517902238002446 , -2.8638546553903597 ]), { 5, 47, 16, 19, 27, 29 })
g.add_vertex( 9 , np.array([ -2.773442183869169 , -0.41710578333825943 ]), { 49, 34, 39, 42, 45, 14, 15 })
g.add_vertex( 10 , np.array([ -2.6513148511799614 , 2.206734312017688 ]), { 37, 38, 6, 12, 18 })
g.add_vertex( 11 , np.array([ -1.9953103499711822 , -2.8745741575040595 ]), { 4, 40, 14, 48, 49 })
g.add_vertex( 12 , np.array([ -3.9222213648123394 , 2.486599969251361 ]), { 46, 10, 6 })
g.add_vertex( 13 , np.array([ 2.9968288404821584 , 3.2037726121371577 ]), { 32, 26, 22 })
g.add_vertex( 14 , np.array([ -1.699649899683311 , -1.7810655323331028 ]), { 49, 34, 9, 11 })
g.add_vertex( 15 , np.array([ -3.944669971760856 , -0.5698903069132717 ]), { 9, 42, 4, 45 })
g.add_vertex( 16 , np.array([ 2.3090490856662207 , -2.858946910034104 ]), { 1, 19, 5, 21, 8 })
g.add_vertex( 17 , np.array([ 4.648321882461582 , -4.0406459617805695 ]), { 1, 2 })
g.add_vertex( 18 , np.array([ -2.4303303146727906 , 1.3023283846958664 ]), { 24, 10, 37, 39 })
g.add_vertex( 19 , np.array([ 2.126963526077005 , -2.346783901345397 ]), { 16, 5, 8, 27 })
g.add_vertex( 20 , np.array([ 0.4790210129242647 , 2.5938223776525655 ]), { 0, 33, 7 })
g.add_vertex( 21 , np.array([ 3.5599520598366006 , -2.285455295523291 ]), { 16, 1, 2, 43 })
g.add_vertex( 22 , np.array([ 2.044436924986556 , 1.613561612129562 ]), { 36, 7, 13, 26, 28 })
g.add_vertex( 23 , np.array([ -0.6584672460824255 , 0.9853508761866232 ]), { 41, 37, 30 })
g.add_vertex( 24 , np.array([ -3.775041788656498 , 0.9663951133505906 ]), { 18, 6, 39, 45 })
g.add_vertex( 25 , np.array([ 4.508668854351654 , -0.22605041963252237 ]), { 43, 31 })
g.add_vertex( 26 , np.array([ 3.1558618433251198 , 2.2088620063567657 ]), { 28, 13, 22 })
g.add_vertex( 27 , np.array([ 0.6801844621275324 , -0.963149335454669 ]), { 19, 8, 41, 30, 47 })
g.add_vertex( 28 , np.array([ 2.2606582462556055 , 0.6187114759417636 ]), { 36, 22, 26, 31 })
g.add_vertex( 29 , np.array([ 0.9254224900584571 , -3.665306178240859 ]), { 35, 5, 8, 44 })
g.add_vertex( 30 , np.array([ 5.625299460465527e-05 , 0.24066046347453085 ]), { 27, 23 })
g.add_vertex( 31 , np.array([ 3.6923947753801922 , 1.0006803091166914 ]), { 25, 3, 28 })
g.add_vertex( 32 , np.array([ 4.392630248072511 , 2.704747186580584 ]), { 3, 13 })
g.add_vertex( 33 , np.array([ 1.0875352723944989 , 3.625947614786792 ]), { 0, 20, 7 })
g.add_vertex( 34 , np.array([ -1.4269325021124981 , -0.4917729562318396 ]), { 9, 14 })
g.add_vertex( 35 , np.array([ -0.3772657441456939 , -4.2229785004289075 ]), { 48, 40, 44, 29 })
g.add_vertex( 36 , np.array([ 1.0592484578020933 , 1.148418797167995 ]), { 28, 22, 7 })
g.add_vertex( 37 , np.array([ -1.7049440674266503 , 1.9830765697219173 ]), { 18, 23, 38, 39, 10 })
g.add_vertex( 38 , np.array([ -1.4966594588653659 , 2.627260420276585 ]), { 0, 37, 10 })
g.add_vertex( 39 , np.array([ -2.8252284081471135 , 0.9078038042714462 ]), { 24, 9, 18, 37 })
g.add_vertex( 40 , np.array([ -2.882495018246267 , -4.8650639562280835 ]), { 48, 35, 4, 11 })
g.add_vertex( 41 , np.array([ 0.5036444861573823 , 0.733014910889465 ]), { 27, 23, 7 })
g.add_vertex( 42 , np.array([ -4.815674631597152 , -0.989495915121795 ]), { 4, 9, 45, 15 })
g.add_vertex( 43 , np.array([ 3.829534553738558 , -1.6736908633226815 ]), { 25, 21 })
g.add_vertex( 44 , np.array([ 1.4442423396340036 , -4.778481756420228 ]), { 2, 35, 29 })
g.add_vertex( 45 , np.array([ -3.4746726165185238 , -0.08815533961032784 ]), { 24, 9, 42, 15 })
g.add_vertex( 46 , np.array([ -4.730374290160427 , 2.2021087454050514 ]), { 12, 6 })
g.add_vertex( 47 , np.array([ 0.4874043117111668 , -2.181609221182633 ]), { 8, 27 })
g.add_vertex( 48 , np.array([ -1.7954928556391172 , -4.37279766240351 ]), { 40, 35, 11 })
g.add_vertex( 49 , np.array([ -2.4344656904621473 , -1.8213084234226193 ]), { 4, 9, 11, 14 })
a =  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44] 
s =  {0: 21, 1: 5, 2: 32, 3: 8, 4: 26, 5: 18, 6: 45, 7: 46, 8: 35, 9: 34, 10: 22, 11: 37, 12: 1, 13: 6, 14: 10, 15: 28, 16: 39, 17: 3, 18: 0, 19: 2, 20: 19, 21: 13, 22: 49, 23: 47, 24: 27, 25: 40, 26: 17, 27: 44, 28: 33, 29: 29, 30: 48, 31: 24, 32: 41, 33: 11, 34: 42, 35: 15, 36: 23, 37: 9, 38: 36, 39: 38, 40: 31, 41: 30, 42: 14, 43: 7, 44: 25} 
t =  {0: 41, 1: 38, 2: 16, 3: 37, 4: 12, 5: 8, 6: 0, 7: 48, 8: 47, 9: 34, 10: 11, 11: 42, 12: 23, 13: 24, 14: 3, 15: 35, 16: 32, 17: 49, 18: 20, 19: 30, 20: 5, 21: 39, 22: 1, 23: 19, 24: 28, 25: 14, 26: 18, 27: 21, 28: 46, 29: 45, 30: 7, 31: 27, 32: 33, 33: 43, 34: 36, 35: 44, 36: 2, 37: 10, 38: 17, 39: 15, 40: 22, 41: 31, 42: 9, 43: 4, 44: 40}


solution = None

solver = PushAndRotate(g, a, s, t)
success, solution = solver.solve()
valid = is_valid_solution(g,a,s,t,solution)
print("Success:", success, "; Valid: ", valid)
if not valid or not success:
    random_generator.print_graph(vert_num, positions, all_neighbours)
    print(a, s, t)

visualizer.draw(g, s, solution)


