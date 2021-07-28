import numpy as np

class Graph:
    
    def __init__(self):
        raise NotImplementedError

    def add_vertex(v_id, position, neighbours):
        raise NotImplementedError

    def get_vertex_position(v_id):
        raise NotImplementedError

    def get_euclidian_distance(v1_id, v2_id):
        raise NotImplementedError

    def get_neighbours(v_id):
        raise NotImplementedError


    

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
