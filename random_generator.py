import random
import kdtree
import numpy as np


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




min_dist = 0.5
min_x = -5
max_x = 5
min_y = -5
max_y = 5
vert_num = 10
neighbours_num = 3
i = 0


x = random.uniform(min_x, max_x)
y = random.uniform(min_y, max_y)
p = Vertex(x, y, i)
kd_tree = kdtree.create([p])

positions = dict()
all_neighbours = dict()

positions[i] = p.coords


while i < vert_num-1:
    x = random.uniform(min_x, max_x)
    y = random.uniform(min_y, max_y)
    p = Vertex(x, y, i+1)
    neighbour = kd_tree.search_nn(p.coords, dist= lambda x, y : np.linalg.norm(x - y))
    if neighbour is None or neighbour[1] > min_dist:
        kd_tree.add(p)
        positions[i+1] = p.coords
        i += 1  

for v_id, coord in positions.items():
    neighbours = kd_tree.search_knn(coord, neighbours_num + 1, dist= lambda x, y : np.linalg.norm(x - y))
    neighbours_id = [v[0].data.v_id for v in neighbours]
    all_neighbours[v_id] = neighbours_id[1:]


for i in range(vert_num):
    print("g.add_vertex(", i, ", np.array([", positions[i][0], ",", positions[i][1], "]), {", ', '.join([str(n) for n in all_neighbours[i]]),"})")    

    

