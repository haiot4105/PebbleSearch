import numpy as np
from scipy.spatial import KDTree


class Graph:

    def __init__(self, positions, all_neighbours):
        self.curr_id = 0
        self.vertices = set()
        self.neighbours = dict()
        self.positions = positions
        self.edges = set()
        self.degreegeq3 = set()

        self.from_kd_ids = dict()
        self.to_kd_ids = dict()
        kd_pos = np.zeros((len(self.positions), 2))

        kd_id = 0
        for v_id, pos in self.positions.items():
            kd_pos[kd_id] = pos
            self.from_kd_ids[kd_id] = v_id
            self.to_kd_ids[v_id] = kd_id
            kd_id += 1

        for v_id in positions:
            self.vertices.add(v_id)
            neighbours = all_neighbours[v_id]
            self.neighbours.update({v_id: neighbours})
            if len(neighbours) >= 3:
                self.degreegeq3.add(v_id)
            for n_id in neighbours:
                if ((v_id, n_id) not in self.edges) and ((n_id, v_id) not in self.edges):
                    self.edges.add((v_id, n_id))

        self.kd_tree = KDTree(kd_pos)

    def get_vertex_position(self, v_id):
        return self.positions[v_id]

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges

    def get_euclidian_distance(self, v1_id, v2_id):
        return np.linalg.norm(self.positions[v1_id] - self.positions[v2_id])

    def get_neighbours(self, v_id):
        return self.neighbours[v_id]

    def __iter__(self):
        return iter(self.vertices)

    def get_vertices_degree_geq_3(self):
        return self.degreegeq3

    def remove_edge(self, v1_id, v2_id):
        self.neighbours[v1_id].discard(v2_id)
        self.neighbours[v2_id].discard(v1_id)
        self.edges.discard((v1_id, v2_id))
        self.edges.discard((v2_id, v1_id))
        if v1_id in self.degreegeq3 and len(self.neighbours[v1_id]) < 3:
            self.degreegeq3.discard(v1_id)
        if v2_id in self.degreegeq3 and len(self.neighbours[v2_id]) < 3:
            self.degreegeq3.discard(v2_id)

    def all_vertices_is_degree_2(self):
        for _, ns in self.neighbours.items():
            if len(ns) > 2:
                return False
        return True

    def get_vertices_in_zone(self, center, size):
        return [self.from_kd_ids[kd_id] for kd_id in self.kd_tree.query_ball_point(center, size)]


class Node:

    def __init__(self, vertex_id, g=0, h=0, F=None, parent=None):
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

    def __lt__(self, other):  # self < other (self has higher priority)
        return self.F < other.F or ((self.F == other.F) and (self.h < other.h))
