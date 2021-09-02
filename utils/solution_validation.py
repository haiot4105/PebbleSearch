import copy

def is_valid_solution(graph, agents, starts, goals, solution):
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
			print("Error: move to vertex withou edge!", agent, v_from, v_to)
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