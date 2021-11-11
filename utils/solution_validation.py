import context
import copy
from .geom import dist_point_line_segment
from pebble_search import Graph
from typing import Dict

def is_valid_solution(graph, agents, starts, goals, solution, size, check_size = True):
	if solution is None:
		print("Solution not found")

	agents_positions = copy.deepcopy(starts)
	reached_goals = set()
	empty_vertices = copy.deepcopy(graph.vertices)
	occupied_vertices = dict()

	for agent, vert in starts.items():
		occupied_vertices.update({vert: agent})
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
			print("Error: move to vertex without edge!", agent, v_from, v_to)
			return False
		if check_size and  not check_collision(graph, v_from, v_to, size, occupied_vertices):
			print("Error: move to vertex with collision!", agent, v_from, v_to)
			return False
		empty_vertices.add(v_from)
		empty_vertices.remove(v_to)
		occupied_vertices.update({v_to: agent})
		occupied_vertices.pop(v_from)
		agents_positions[agent] = v_to

	for agent, pos in agents_positions.items():
		if pos != goals[agent]:
			print("Agent", agent, "doesnt reach goal")
			return False
	return True


def check_suspect_vertex(graph: Graph, edge_p1, edge_p2, suspect_v, size) -> bool:
	suspect_p = graph.get_vertex_position(suspect_v)
	if dist_point_line_segment(edge_p1, edge_p2, suspect_p) < 2 * size:
		return True
	return False


def check_collision(graph: Graph, v_from: int, v_to: int, size: float, occupied_vertices: Dict[int, int]) -> bool:
	edge_len = graph.get_euclidian_distance(v_from, v_to)
	p_from = graph.get_vertex_position(v_from)
	p_to = graph.get_vertex_position(v_to)
	suspect_zone_size = edge_len + 2 * size
	suspect_vert = graph.get_vertices_in_zone(graph.get_vertex_position(v_from), suspect_zone_size)
	for v in suspect_vert:
		if v == v_from or v == v_to:
			continue
		if check_suspect_vertex(graph, p_from, p_to, v, size) and v in occupied_vertices:
			return False
	return True
