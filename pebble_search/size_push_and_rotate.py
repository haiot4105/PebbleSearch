from .pathplanner import shortest_path
from .pathplanner import path_to_closest_empty_vertex
from .geom import dist_point_line_segment

import numpy as np
import copy


class PushAndRotateWithSizes:

    def __init__(self, graph, agents, starts, goals, sizes):
        self.graph = graph
        self.agents = agents
        self.starts = starts
        self.goals = goals
        self.sizes = sizes
        self.max_size = max(sizes)

        self.agents_positions = copy.deepcopy(starts)
        self.reached_goals = set()
        self.successful_agents = set()
        self.empty_vertices = copy.deepcopy(graph.vertices)
        self.occupied_vertices = dict()

        for agent, vert in starts.items():
            self.occupied_vertices.update({vert: agent})
            self.empty_vertices.discard(vert)

        # print(self.graph.positions)
        # print(self.graph.neighbours)
        self.debug_prefix = ""

    def solve(self):
        solution = []

        for agent in self.agents:
            queue = []
            if self.graph.all_vertices_is_degree_2():
                if not self.plan_polygon(solution, agent):
                    return False, None
            else:
                if not self.plan(solution, agent, queue):
                    return False, None

        return True, solution

    def plan_polygon(self, solution, agent):
        # TODO
        return False

    def plan(self, solution, agent, queue):
        # print("(plan) Start")
        p_exists, p = shortest_path(self.graph, self.agents_positions[agent], self.goals[agent], {})
        # print(p)
        if not p_exists:
            print("Global path for agent", agent, "not found")
            return False
        queue.append(p.pop())

        while self.agents_positions[agent] != self.goals[agent]:
            v = p.pop()

            if v in queue:
                rotate_res, queue = self.rotate(solution, queue, v)
                if not rotate_res:
                    return False
            else:
                if not self.push(solution, agent, v, self.successful_agents_positions()):
                    print(self.occupied_vertices)
                    if v not in self.occupied_vertices:
                        return False
                    if not self.swap(solution, agent, self.occupied_vertices[v]):
                        return False

            queue.append(v)
        # print(queue)
        self.agent_achive_goal(agent)
        resolve_res = self.resolve(solution, queue)
        # print("(plan) End")
        return resolve_res

    def push(self, solution, agent, v, blocked):
        # print("(push) Start")
        if v in self.occupied_vertices:
            tmp_blocked = blocked | {self.agents_positions[agent]}

            if not self.clear_vertex(solution, v, tmp_blocked):
                return False

        return self.try_move_agent(solution, agent, self.agents_positions[agent], v)


    def clear_vertex(self, solution, v, blocked):
        # print("(clear_vertex) Start")

        if v in blocked:
            return False

        p_exists, p = path_to_closest_empty_vertex(self.graph, v, self.empty_vertices, blocked)
        if not p_exists:
            return False

        v2 = p.pop(0)
        while v != v2:
            v1 = p.pop(0)
            r1 = self.occupied_vertices[v1]
            # TODO roll back solution
            if not self.try_move_agent(solution, r1, v1, v2):
                return False
            v2 = v1
        return True

    def swap(self, solution, agent_1, agent_2):
        # print("(swap) Start", agent_1, agent_2)

        s = self.graph.get_vertices_degree_geq_3()
        commited_state = self.commit_state()

        for v in s:
            tmp_solution = []
            self.rollback_state(commited_state)
            if self.multipush(tmp_solution, agent_1, agent_2, v):
                if self.clear(tmp_solution, agent_1, agent_2, v):
                    tmp_solution_2 = []
                    tmp_solution_2 += tmp_solution
                    if self.exchange(tmp_solution_2, agent_1, agent_2, v):
                        if self.reverse(tmp_solution_2, tmp_solution, agent_1, agent_2):
                            solution += tmp_solution_2
                    # print("(swap) End")
                    return True

        return False

    def multipush(self, solution, agent_1, agent_2, v):
        # print("(multipush) Start")
        p_exists, p = shortest_path(self.graph, self.agents_positions[agent_1], v, {})

        if not p_exists:
            return False
        if len(p) < 2:
            return True
        p.pop()

        if p[-1] in self.occupied_vertices and (self.occupied_vertices[p[-1]] == agent_2):
            r = agent_2
            s = agent_1
            p.pop()
        else:
            r = agent_1
            s = agent_2

        for waypoint in reversed(p):
            v_r = self.agents_positions[r]
            v_s = self.agents_positions[s]

            if waypoint in self.occupied_vertices:
                blocked = {v_r, v_s}
                if not self.clear_vertex(solution, waypoint, blocked):
                    return False

            if not self.try_move_agent(solution, r, v_r, waypoint) or not self.try_move_agent(solution, s, v_s, v_r):
                return False

        return True

    def clear(self, solution, agent_1, agent_2, v):
        # print("(clear) Start")
        neighbours = self.graph.get_neighbours(v)
        empty_neighbours = neighbours & self.empty_vertices

        if len(empty_neighbours) > 1:
            return True

        if self.agents_positions[agent_1] == v:
            r = agent_1
            s = agent_2
            v1 = self.agents_positions[s]
        elif self.agents_positions[agent_2] == v:
            r = agent_2
            s = agent_1
            v1 = self.agents_positions[s]
        else:
            print("Error before swap clear")
            exit(-1)

        for n in neighbours:
            if (n in empty_neighbours) or (n == v1):
                continue
            if self.clear_vertex(solution, n, empty_neighbours | {v, v1}):
                if len(empty_neighbours) > 0:
                    return True
                empty_neighbours.add(n)

        if len(empty_neighbours) == 0:
            return False

        eps = empty_neighbours.pop()
        commited_state = self.commit_state()

        for n in neighbours:
            if (n == eps) or (n == v1):
                continue
            tmp_solution = []
            self.rollback_state(commited_state)
            if self.clear_vertex(tmp_solution, n, {v, v1}):
                if self.clear_vertex(tmp_solution, eps, {v, v1, n}):
                    solution += tmp_solution
                    return True
                break

        for n in neighbours:
            if (n == eps) or (n == v1):
                continue
            tmp_solution = []
            self.rollback_state(commited_state)
            if not self.try_move_agent(tmp_solution, r, self.agents_positions[r], eps) or not self.try_move_agent(tmp_solution, s, self.agents_positions[s], v):
                continue

            if self.clear_vertex(tmp_solution, n, {v, eps}):
                if self.clear_vertex(tmp_solution, v1, {v, eps, n}):
                    solution += tmp_solution
                    return True
                break

        if not self.clear_vertex(solution, v1, {v}):
            return False

        if not self.try_move_agent(solution, r, self.agents_positions[r], v1):
            return False

        if not self.clear_vertex(solution, eps, {v, v1, self.agents_positions[s]}):
            return False

        n = neighbours.pop()
        while True:
            if (n != v1) and (n != eps):
                break
            n = neighbours.pop()

        t = self.occupied_vertices[n]

        if not self.try_move_agent(solution, t, n, v):
            return False
        if not self.try_move_agent(solution, t, v, eps):
            return False
        if not self.try_move_agent(solution, r, self.agents_positions[r], v):
            return False
        if not self.try_move_agent(solution, s, self.agents_positions[s], v1):
            return False

        return self.clear_vertex(solution, eps, {v, v1, n})

    def exchange(self, solution, agent_1, agent_2, v):
        # print("(exchange) Start")
        if self.agents_positions[agent_1] == v:
            r = agent_1
            s = agent_2
        elif self.agents_positions[agent_2] == v:
            r = agent_2
            s = agent_1
        else:
            print("Error! Something went wrong before clear in swap")
            exit(-1)

        neighbours = self.graph.get_neighbours(v)
        empty_neighbours = neighbours & self.empty_vertices

        if len(empty_neighbours) < 2:
            print("Error! Less then 2 empty neighbours after clear in swap")
            exit(-1)

        v1 = empty_neighbours.pop()
        v2 = empty_neighbours.pop()
        v_s = self.agents_positions[s]
        if not self.try_move_agent(solution, r, v, v1):
            return False
        if not self.try_move_agent(solution, s, v_s, v):
            return False
        if not self.try_move_agent(solution, s, v, v2):
            return False
        if not self.try_move_agent(solution, r, v1, v):
            return False
        if not self.try_move_agent(solution, r, v, v_s):
            return False
        if not self.try_move_agent(solution, s, v2, v):
            return False
        return True

    def circular_buffer_index(self, ind, buff_len):
        if ind < 0:
            return -(abs(ind) % buff_len)
        else:
            return abs(ind) % buff_len

    def rotate(self, solution, queue, v):
        # print("(rotate) Start")
        v_index = queue.index(v)
        c = queue[v_index:]
        queue = queue[:v_index]

        for ind, v1 in enumerate(c):
            if v1 not in self.occupied_vertices:

                i_move_from = self.circular_buffer_index(ind - 1, len(c))
                i_move_to = self.circular_buffer_index(ind, len(c))

                while True:
                    move_from = c[i_move_from]
                    move_to = c[i_move_to]
                    if move_from in self.occupied_vertices:
                        if not self.try_move_agent(solution, self.occupied_vertices[move_from], move_from, move_to):
                            return False, None
                    i_move_to = self.circular_buffer_index(i_move_from, len(c))
                    i_move_from = self.circular_buffer_index(i_move_from - 1, len(c))

                    if c[i_move_from] == v1:
                        break
                return True, queue

        for ind, v1 in enumerate(c):
            r = self.occupied_vertices[v1]
            tmp_solution = []

            set_c = set(c)
            set_c.discard(v1)

            if self.clear_vertex(tmp_solution, v1, set_c):
                # print(c)
                solution += tmp_solution
                v2 = c[ind - 1]
                r2 = self.occupied_vertices[v2]
                if not self.try_move_agent(solution, r2, v2, v1):
                    return False, None

                if not self.swap(solution, r, r2):
                    return False, None

                i_move_from = self.circular_buffer_index(ind - 2, len(c))
                i_move_to = self.circular_buffer_index(ind - 1, len(c))

                while True:
                    move_from = c[i_move_from]
                    move_to = c[i_move_to]
                    if not self.try_move_agent(solution, self.occupied_vertices[move_from], move_from, move_to):
                        return False, None
                    i_move_to = self.circular_buffer_index(i_move_from, len(c))
                    i_move_from = self.circular_buffer_index(i_move_from - 1, len(c))

                    if c[i_move_from] == v2:
                        break

                self.reverse(solution, tmp_solution, r, r2)
                return True, queue
        return False, None

    def resolve(self, solution, queue):

        # print("(resolve) Start")

        while len(queue) > 0:
            v = queue[-1]
            # print(v)
            if v in self.occupied_vertices:
                r = self.occupied_vertices[v]
                if r in self.successful_agents and self.agents_positions[r] != self.goals[r]:
                    if not self.push(solution, r, self.goals[r], self.successful_agents_positions()):
                        s = self.occupied_vertices[self.goals[r]]
                        # print("(resolve) Rec")
                        return self.plan(solution, s, queue)
            queue.pop()
        # print("(resolve) End")
        return True

    def reverse(self, solution, tail, agent_1=None, agent_2=None):
        # print("(reverse) Start")

        for move in reversed(tail):
            if agent_1 is not None and move[0] == agent_1:
                if not self.try_move_agent(solution, agent_2, move[2], move[1]):
                    return False
            elif agent_2 is not None and move[0] == agent_2:
                if not self.try_move_agent(solution, agent_1, move[2], move[1]):
                    return False
            else:
                self.move_agent(solution, move[0], move[2], move[1])
        return True

    def move_agent(self, solution, agent, v_from, v_to):
        # print("\t(move) Agent:", agent, "from", v_from, "to", v_to)
        self.check_move(agent, v_from, v_to)
        self.empty_vertices.add(v_from)
        self.empty_vertices.remove(v_to)
        self.occupied_vertices.update({v_to: agent})
        self.occupied_vertices.pop(v_from)
        self.agents_positions[agent] = v_to
        solution.append((agent, v_from, v_to))

    def agent_achive_goal(self, agent):
        self.reached_goals.add(self.goals[agent])
        self.successful_agents.add(agent)

    def commit_state(self):
        tmp_empty = copy.deepcopy(self.empty_vertices)
        tmp_occup = copy.deepcopy(self.occupied_vertices)
        tmp_pos = copy.deepcopy(self.agents_positions)

        return (tmp_empty, tmp_occup, tmp_pos)

    def rollback_state(self, state):
        self.empty_vertices = copy.deepcopy(state[0])
        self.occupied_vertices = copy.deepcopy(state[1])
        self.agents_positions = copy.deepcopy(state[2])

    def successful_agents_positions(self):
        return set([self.agents_positions[a] for a in self.successful_agents])

    def try_move_agent(self, solution, agent, v_from, v_to):
        # print("\t(try move) Agent:", agent, "from", v_from, "to", v_to)
        tmp_solution = []
        if self.clear_edge(tmp_solution, agent, v_from, v_to):
            solution += tmp_solution
            self.move_agent(solution, agent, v_from, v_to)
            self.reverse(solution, tmp_solution)
            return True
        else:
            return False

    def clear_edge(self, solution, agent, v_from, v_to):
        blocked = {v_from}
        unoccupied_blocked = {v_to}
        commited_state = self.commit_state()
        for v in self.get_interfere_vertices(agent, v_from, v_to):
            if v in self.occupied_vertices and \
                    not self.clear_interfere_vertex(solution, v, blocked, unoccupied_blocked, agent, self.occupied_vertices[v], v_from, v_to):
                self.rollback_state(commited_state)
                return False
            unoccupied_blocked.add(v)
        return True

    def clear_interfere_vertex(self, solution, v, blocked, unoccupied_blocked, agent_1, agent_2, v_from, v_to, rec=False ):
        if v in blocked:
            return False
        tmp_empty = set()
        for eps in self.empty_vertices:
            if eps in unoccupied_blocked:
                continue
            p_from = self.graph.get_vertex_position(v_from)
            p_to = self.graph.get_vertex_position(v_to)
            if self.check_suspect_vertex(p_from, p_to, eps, agent_1, agent_2):
                continue
            tmp_empty.add(eps)

        tmp_graph = copy.deepcopy(self.graph)
        for n in self.graph.get_neighbours(v):
            p1 = self.graph.get_vertex_position(v)
            p2 = self.graph.get_vertex_position(n)
            if self.check_suspect_vertex(p1, p2, v_from, agent_2, agent_1):
                tmp_graph.remove_edge(v, n)

        p_exists, p = path_to_closest_empty_vertex(tmp_graph, v, tmp_empty, blocked)

        if not p_exists:
            if rec:
                return False
            p_exists, p = path_to_closest_empty_vertex(self.graph, v, tmp_empty, blocked)
            if not p_exists:
                return False
            blocked = {v}
            unoccupied_blocked = {p[-2]}
            last_try = self.clear_interfere_vertex([], v_from, blocked,unoccupied_blocked, agent_2, agent_1, v, p[-2], True)
            if not last_try:
                return False
        print(p)
        v_to = p.pop(0)
        while v != v_to:
            v_from = p.pop(0)
            if v_from in self.occupied_vertices:
                agent = self.occupied_vertices[v_from]
                if not self.try_move_agent(solution, agent, v_from, v_to):
                    return False
                v_to = v_from
            else:
                # TODO fix bug with tmp_path
                tmp_path = [v_to, v_from]
                tmp_v = p.pop(0)
                while True:
                    if tmp_v in self.occupied_vertices:
                        break
                    tmp_path.append(tmp_v)
                    tmp_v = p.pop(0)

                print(tmp_path)
                tmp_v_from = tmp_v
                tmp_v_to = tmp_path.pop()
                agent = self.occupied_vertices[tmp_v_from]
                while True:
                    if not self.try_move_agent(solution, agent, tmp_v_from, tmp_v_to):
                        return False
                    if tmp_v_to == v_to:
                        v_to = tmp_v
                        break
                    tmp_v_from = tmp_v_to
                    tmp_v_to = tmp_path.pop()
        return True

    def get_interfere_vertices(self, agent, v_from, v_to):
        result = set()
        edge_len = self.graph.get_euclidian_distance(v_from, v_to)
        p_from = self.graph.get_vertex_position(v_from)
        p_to = self.graph.get_vertex_position(v_to)
        suspect_vert = self.graph.get_vertices_in_zone(self.graph.get_vertex_position(v_from),
                                                       edge_len + self.sizes[agent] + self.max_size)
        for v in suspect_vert:
            if v == v_from:
                continue
            if v in self.occupied_vertices and \
                    self.check_suspect_vertex(p_from, p_to, v, agent, self.occupied_vertices[v]):
                result.add(v)
        return result

    def check_suspect_vertex(self, edge_p1, edge_p2, suspect_v, edge_agent, suspect_agent):
        suspect_p = self.graph.get_vertex_position(suspect_v)
        if dist_point_line_segment(edge_p1, edge_p2, suspect_p) < self.sizes[edge_agent] + self.sizes[suspect_agent]:
            return True
        return False

    def check_move(self, agent, v_from, v_to):
        if self.agents_positions[agent] != v_from:
            print(self.debug_prefix, "Error: move from incorrect position!", agent, v_from, v_to)
            exit()
        if v_to in self.occupied_vertices:
            print(self.debug_prefix, "Error: move to occupied position!", agent, v_from, v_to)
            exit()
        if v_to not in self.graph.get_neighbours(v_from):
            print(self.debug_prefix, "Error: move to vertex withou edge!", agent, v_from, v_to)
            exit()

        # if self.goals[agent] == v_from and v_from in self.reached_goals:
        #     print(self.debug_prefix,  "Alert! Agent ", agent, "moved from goal!")
        # if self.goals[agent] == v_to and v_to in self.reached_goals:
        #     print(self.debug_prefix,  "Alert! Agent ", agent, "moved back to goal!")

