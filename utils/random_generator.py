import random
import kdtree
import numpy as np
from . import biconnected


class Vertex:
    def __init__(self, x, y, v_id):
        self.coords = np.array([x, y])
        self.v_id = v_id

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, i):
        return self.coords[i]

    def __repr__(self):
        return 'Item({}, {}, {})'.format(self.coords[0], self.coords[1], self.v_id)

def generate_random_graph(min_dist = 0.5, min_x = -5, max_x = 5, min_y = -5, max_y = 5, vert_num = 30, neighbours_max_num = 5):
    tries = 1
    
    while True:
        print(tries)
        i = 0
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        p = Vertex(x, y, i)
        kd_tree = kdtree.create([p])
        positions = dict()
        all_neighbours = dict()
        positions[i] = p.coords

        print("A")
        while i < vert_num-1:
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            p = Vertex(x, y, i+1)
            neighbour = kd_tree.search_nn(p.coords, dist= lambda x, y : np.linalg.norm(x - y))
            if neighbour is None or neighbour[1] > min_dist:
                kd_tree.add(p)
                positions[i+1] = p.coords
                i += 1  
        print("B")
        for v_id, coord in positions.items():
            neighbours_num = random.randint(2, neighbours_max_num) - len(all_neighbours.get(v_id, []))
            if neighbours_num > 0:
                neighbours = kd_tree.search_knn(coord, neighbours_num + 1, dist= lambda x, y : np.linalg.norm(x - y))
                neighbours_id = [v[0].data.v_id for v in neighbours]
                all_neighbours[v_id] = all_neighbours.get(v_id, set()) | set(neighbours_id[1:])
                for n in neighbours_id[1:]:
                    if n not in all_neighbours:
                        all_neighbours[n] = {v_id}
                    else:
                        all_neighbours[n].add(v_id)
        print("C")
        edges = set()
        graph_for_checking = biconnected.Graph(vert_num)

        for v_id in range(vert_num):
            neighbours = all_neighbours[v_id]
            for n_id in neighbours:
                if ((v_id, n_id) not in edges) and ((n_id, v_id) not in edges):
                    edges.add((v_id, n_id))
                    graph_for_checking.addEdge(v_id, n_id)

        print("D")
        graph_for_checking.BCC()

        print("Components 1:", graph_for_checking.count)

        if graph_for_checking.count == 1:
            print("Components 11:", graph_for_checking.count)
            return positions, all_neighbours
        
        tries += 1
        
        # print(positions, all_neighbours)
        



def generate_random_agents(agents_num = 20, vert_num = 30):

    if agents_num > vert_num-2:
        raise ValueError

    starts = dict()
    goals = dict()

    starts_set = set()
    goals_set = set()

    a = 0
    while a < agents_num:
        start = random.randint(0, vert_num-1)
        goal = random.randint(0, vert_num-1)
        
        if start in starts_set or goal in goals_set:
            continue

        starts_set.add(start)
        goals_set.add(goal)

        starts[a] = start
        goals[a] = goal
        a += 1 

    return list(range(agents_num)), starts, goals


def print_graph(vert_num, positions, all_neighbours):
    for i in range(vert_num):
        print("g.add_vertex(", i, ", np.array([", positions[i][0], ",", positions[i][1], "]), {", ', '.join([str(n) for n in all_neighbours[i]]),"})")    