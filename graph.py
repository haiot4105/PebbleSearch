import numpy as np

class Graph:
    
    def __init__(self):
        self.curr_id = 0
        self.verticies = set()
        self.neighbours = dict()
        self.positions = dict()
        self.edges = set()
        self.degreegeq3 = set()

    def add_vertex(self, v_id, position, neighbours):
        self.verticies.add(v_id)
        self.neighbours.update({v_id : neighbours})
        if len(neighbours) >= 3:
            self.degreegeq3.add(v_id)
        for n_id in neighbours:
            if ((v_id, n_id) not in self.edges) and ((n_id, v_id) not in self.edges):
                self.edges.add((v_id, n_id))

        self.positions.update({v_id : position})

    def get_vertex_position(self, v_id):
        return self.positions[v_id]

    def get_verticies(self):
        return self.verticies

    def get_edges(self):
        return self.edges

    def get_euclidian_distance(self, v1_id, v2_id):
        return np.linalg.norm(self.positions[v1_id] - self.positions[v2_id])

    def get_neighbours(self, v_id):
        return self.neighbours[v_id]

    def __iter__(self):
        return iter(self.verticies)

    def get_verticies_degree_geq_3(self):
        return self.degreegeq3

  
class Node:

    def __init__(self, vertex_id, g = 0, h = 0, F = None, parent = None):
        self.v_id = vertex_id
        self.g = g
        self.h = h
        if F is None:
            self.F = self.g + h
        else:
            self.F = F        
        self.parent = parent

    def __eq__(self, other):
        return self.v_id == other.v_id

    def __lt__(self, other): #self < other (self has higher priority)
        return self.F < other.F or ((self.F == other.F) and (self.h < other.h))
