from .pathplanner import shortest_path
from .pathplanner import path_to_closest_empty_vertex
from .geom import dist_point_line_segment
from .graph import Graph

from typing import Dict, Set, List, Tuple
import numpy as np
import copy


class PushAndRotateWithSizes:

    def __init__(self, graph, agents, starts, goals, size):
        self._graph: Graph = graph
        self._agents: Dict[int, int] = agents
        self._starts: Dict[int, int] = starts
        self._goals: Dict[int, int] = goals
        self._size: float = size

        self._agents_positions: Dict[int, int] = copy.deepcopy(starts)
        self._reached_goals: Set[int] = set()
        self._successful_agents: Set[int] = set()
        self._empty_vertices: Set[int] = copy.deepcopy(graph.get_vertices())
        self._occupied_vertices: Dict[int, int] = dict()
        self._deadlock_edges: Set[Tuple[int, int]] = self.find_deadlock_edges()
        self._graph_deadlock_free: Graph = copy.deepcopy(self._graph)
        print(self._deadlock_edges)
        for e in self._deadlock_edges:
            self._graph_deadlock_free.discard_edge(*e)

        for agent, vert in starts.items():
            self._occupied_vertices.update({vert: agent})
            self._empty_vertices.discard(vert)


    def solve(self):
        solution = []

        for agent in self._agents:
            queue = []
            if self._graph.all_vertices_is_degree_2():
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

        p_exists, p = shortest_path(self._graph_deadlock_free, self._agents_positions[agent], self._goals[agent], {})
        print(p)
        if not p_exists:
            print("Deadlock free global path for agent", agent, "not found")
            p_exists, p = shortest_path(self._graph, self._agents_positions[agent], self._goals[agent], {})

        if not p_exists:
            print("Global path for agent", agent, "not found")
            return False
        queue.append(p.pop())

        while self._agents_positions[agent] != self._goals[agent]:
            v = p.pop()

            if v in queue:
                rotate_res, queue = self.rotate(solution, queue, v)
                if not rotate_res:
                    return False
            else:
                if not self.push(solution, agent, v, self.successful_agents_positions()):
                    if v not in self._occupied_vertices:
                        return False
                    if not self.swap(solution, agent, self._occupied_vertices[v]):
                        return False

            queue.append(v)
        # print(queue)
        self.agent_achieve_goal(agent)
        resolve_res = self.resolve(solution, queue)
        # print("(plan) End")
        return resolve_res

    def push(self, solution, agent, v, blocked):
        # print("(push) Start")
        if v in self._occupied_vertices:
            tmp_blocked = blocked | {self._agents_positions[agent]}

            if not self.clear_vertex(solution, v, tmp_blocked):
                return False

        return self.try_move_agent(solution, agent, self._agents_positions[agent], v)

    def clear_vertex(self, solution, v, blocked):
        # print("(clear_vertex) Start")

        if v in blocked:
            return False

        p_exists, p = path_to_closest_empty_vertex(self._graph_deadlock_free, v, self._empty_vertices, blocked)
        if not p_exists:
            p_exists, p = path_to_closest_empty_vertex(self._graph, v, self._empty_vertices, blocked)

        if not p_exists:
            return False

        v2 = p.pop(0)
        while v != v2:
            v1 = p.pop(0)
            r1 = self._occupied_vertices[v1]
            # TODO roll back solution
            if not self.try_move_agent(solution, r1, v1, v2):
                return False
            v2 = v1
        return True

    def swap(self, solution, agent_1, agent_2):

        s = self._graph.get_vertices_degree_geq_3()
        committed_state = self.commit_state()

        for v in s:
            tmp_solution = []
            self.rollback_state(committed_state)
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


        p_exists, p = shortest_path(self._graph_deadlock_free, self._agents_positions[agent_1], v, {})

        if not p_exists:
            p_exists, p = shortest_path(self._graph, self._agents_positions[agent_1], v, {})

        if not p_exists:
            return False
        if len(p) < 2:
            return True
        p.pop()

        if p[-1] in self._occupied_vertices and (self._occupied_vertices[p[-1]] == agent_2):
            r = agent_2
            s = agent_1
            p.pop()
        else:
            r = agent_1
            s = agent_2

        for waypoint in reversed(p):
            v_r = self._agents_positions[r]
            v_s = self._agents_positions[s]

            if waypoint in self._occupied_vertices:
                blocked = {v_r, v_s}
                if not self.clear_vertex(solution, waypoint, blocked):
                    return False

            if not self.try_move_agent(solution, r, v_r, waypoint) or not self.try_move_agent(solution, s, v_s, v_r):
                return False

        return True

    def clear(self, solution, agent_1, agent_2, v):
        # print("(clear) Start")
        neighbours = self._graph.get_neighbours(v)
        empty_neighbours = neighbours & self._empty_vertices

        if len(empty_neighbours) > 1:
            return True

        if self._agents_positions[agent_1] == v:
            r = agent_1
            s = agent_2
            v1 = self._agents_positions[s]
        elif self._agents_positions[agent_2] == v:
            r = agent_2
            s = agent_1
            v1 = self._agents_positions[s]
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
        committed_state = self.commit_state()

        for n in neighbours:
            if (n == eps) or (n == v1):
                continue
            tmp_solution = []
            self.rollback_state(committed_state)
            if self.clear_vertex(tmp_solution, n, {v, v1}):
                if self.clear_vertex(tmp_solution, eps, {v, v1, n}):
                    solution += tmp_solution
                    return True
                break

        for n in neighbours:
            if (n == eps) or (n == v1):
                continue
            tmp_solution = []
            self.rollback_state(committed_state)
            if not self.try_move_agent(tmp_solution, r, self._agents_positions[r], eps) or not self.try_move_agent(tmp_solution, s, self._agents_positions[s], v):
                continue

            if self.clear_vertex(tmp_solution, n, {v, eps}):
                if self.clear_vertex(tmp_solution, v1, {v, eps, n}):
                    solution += tmp_solution
                    return True
                break

        if not self.clear_vertex(solution, v1, {v}):
            return False

        if not self.try_move_agent(solution, r, self._agents_positions[r], v1):
            return False

        if not self.clear_vertex(solution, eps, {v, v1, self._agents_positions[s]}):
            return False

        n = neighbours.pop()
        while True:
            if (n != v1) and (n != eps):
                break
            n = neighbours.pop()

        t = self._occupied_vertices[n]

        if not self.try_move_agent(solution, t, n, v):
            return False
        if not self.try_move_agent(solution, t, v, eps):
            return False
        if not self.try_move_agent(solution, r, self._agents_positions[r], v):
            return False
        if not self.try_move_agent(solution, s, self._agents_positions[s], v1):
            return False

        return self.clear_vertex(solution, eps, {v, v1, n})

    def exchange(self, solution, agent_1, agent_2, v):
        # print("(exchange) Start")
        if self._agents_positions[agent_1] == v:
            r = agent_1
            s = agent_2
        elif self._agents_positions[agent_2] == v:
            r = agent_2
            s = agent_1
        else:
            print("Error! Something went wrong before clear in swap")
            exit(-1)

        neighbours = self._graph.get_neighbours(v)
        empty_neighbours = neighbours & self._empty_vertices

        if len(empty_neighbours) < 2:
            print("Error! Less then 2 empty neighbours after clear in swap")
            exit(-1)

        v1 = empty_neighbours.pop()
        v2 = empty_neighbours.pop()
        v_s = self._agents_positions[s]
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
            if v1 not in self._occupied_vertices:

                i_move_from = self.circular_buffer_index(ind - 1, len(c))
                i_move_to = self.circular_buffer_index(ind, len(c))

                while True:
                    move_from = c[i_move_from]
                    move_to = c[i_move_to]
                    if move_from in self._occupied_vertices:
                        if not self.try_move_agent(solution, self._occupied_vertices[move_from], move_from, move_to):
                            return False, None
                    i_move_to = self.circular_buffer_index(i_move_from, len(c))
                    i_move_from = self.circular_buffer_index(i_move_from - 1, len(c))

                    if c[i_move_from] == v1:
                        break
                return True, queue

        for ind, v1 in enumerate(c):
            r = self._occupied_vertices[v1]
            tmp_solution = []

            set_c = set(c)
            set_c.discard(v1)

            if self.clear_vertex(tmp_solution, v1, set_c):
                # print(c)
                solution += tmp_solution
                v2 = c[ind - 1]
                r2 = self._occupied_vertices[v2]
                if not self.try_move_agent(solution, r2, v2, v1):
                    return False, None

                if not self.swap(solution, r, r2):
                    return False, None

                i_move_from = self.circular_buffer_index(ind - 2, len(c))
                i_move_to = self.circular_buffer_index(ind - 1, len(c))

                while True:
                    move_from = c[i_move_from]
                    move_to = c[i_move_to]
                    if not self.try_move_agent(solution, self._occupied_vertices[move_from], move_from, move_to):
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
            if v in self._occupied_vertices:
                r = self._occupied_vertices[v]
                if r in self._successful_agents and self._agents_positions[r] != self._goals[r]:
                    if not self.push(solution, r, self._goals[r], self.successful_agents_positions()):
                        s = self._occupied_vertices[self._goals[r]]
                        # print("(resolve) Rec")
                        return self.plan(solution, s, queue)
            queue.pop()
        # print("(resolve) End")
        return True

    def reverse(self, solution, tail, agent_1=None, agent_2=None):
        for move in reversed(tail):
            if agent_1 is not None and move[0] == agent_1:
                if not self.move_agent(solution, agent_2, move[2], move[1]):
                    return False
            elif agent_2 is not None and move[0] == agent_2:
                if not self.move_agent(solution, agent_1, move[2], move[1]):
                    return False
            else:
                self.move_agent(solution, move[0], move[2], move[1])
        return True

    def move_agent(self, solution, agent, v_from, v_to):
        # print("\t(move) Agent:", agent, "from", v_from, "to", v_to)
        self.check_move(agent, v_from, v_to)
        self._empty_vertices.add(v_from)
        self._empty_vertices.remove(v_to)
        self._occupied_vertices.update({v_to: agent})
        self._occupied_vertices.pop(v_from)
        self._agents_positions[agent] = v_to
        solution.append((agent, v_from, v_to))

    def agent_achieve_goal(self, agent):
        self._reached_goals.add(self._goals[agent])
        self._successful_agents.add(agent)

    def commit_state(self):
        tmp_empty = copy.deepcopy(self._empty_vertices)
        tmp_occupied = copy.deepcopy(self._occupied_vertices)
        tmp_pos = copy.deepcopy(self._agents_positions)

        return (tmp_empty, tmp_occupied, tmp_pos)

    def rollback_state(self, state):
        self._empty_vertices = copy.deepcopy(state[0])
        self._occupied_vertices = copy.deepcopy(state[1])
        self._agents_positions = copy.deepcopy(state[2])

    def successful_agents_positions(self):
        return set([self._agents_positions[a] for a in self._successful_agents])

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
        blocked = {v_from, v_to}
        unoccupied_blocked = set()
        interfere_v = self.get_interfere_vertices(v_from, v_to)

        for v in interfere_v:
            if v not in self._occupied_vertices:
                unoccupied_blocked.add(v)

        committed_state = self.commit_state()
        for v in interfere_v:
            if v in self._occupied_vertices and \
                    not self.clear_interfere_vertex(solution, v, blocked, unoccupied_blocked, v_from, v_to):
                self.rollback_state(committed_state)
                return False
            unoccupied_blocked.add(v)
        return True,

    def clear_interfere_vertex(self, solution, v, blocked, unoccupied_blocked, v_from, v_to):
        tmp_empty = set()
        p_from = self._graph.get_vertex_position(v_from)
        p_to = self._graph.get_vertex_position(v_to)

        for eps in self._empty_vertices:
            if eps in unoccupied_blocked:
                continue
            if self.check_suspect_vertex(p_from, p_to, eps):
                continue
            tmp_empty.add(eps)

        tmp_graph = copy.deepcopy(self._graph)
        tmp_graph_deadlock_free = copy.deepcopy(self._graph_deadlock_free)

        for e in self._graph.get_edges():
            p1 = self._graph.get_vertex_position(e[0])
            p2 = self._graph.get_vertex_position(e[1])
            if self.check_suspect_vertex(p1, p2, v_from) or self.check_suspect_vertex(p1, p2, v_to):
                tmp_graph.discard_edge(*e)
                tmp_graph_deadlock_free.discard_edge(*e)

        p_exists, p = path_to_closest_empty_vertex(tmp_graph_deadlock_free, v, tmp_empty, blocked)

        if not p_exists:
            p_exists, p = path_to_closest_empty_vertex(tmp_graph, v, tmp_empty, blocked)

        if not p_exists:
            return False

        v_to = p.pop(0)
        while v != v_to:
            v_from = p.pop(0)
            if v_from in self._occupied_vertices:
                agent = self._occupied_vertices[v_from]
                if not self.try_move_agent(solution, agent, v_from, v_to):
                    return False
                v_to = v_from
            else:
                tmp_path = [v_to, v_from]
                tmp_v = p.pop(0)
                while True:
                    if tmp_v in self._occupied_vertices:
                        break
                    tmp_path.append(tmp_v)
                    tmp_v = p.pop(0)

                tmp_v_from = tmp_v
                tmp_v_to = tmp_path.pop()
                agent = self._occupied_vertices[tmp_v_from]
                while True:
                    if not self.try_move_agent(solution, agent, tmp_v_from, tmp_v_to):
                        return False
                    if tmp_v_to == v_to:
                        v_to = tmp_v
                        break
                    tmp_v_from = tmp_v_to
                    tmp_v_to = tmp_path.pop()

    def clear_deadlock_edge(self, solution, agent, v_from, v_to):
        cleared = set()
        not_cleared = set()
        blocked = {v_from, v_to}
        unoccupied_blocked = set()
        interfere_v = self.get_interfere_vertices(v_from, v_to)

        for v in interfere_v:
            if v not in self._occupied_vertices:
                unoccupied_blocked.add(v)
                cleared.add(v)

        first_committed_state = self.commit_state()

        committed_state = self.commit_state()

        for v in interfere_v:
            tmp_solution = []
            if v in self._occupied_vertices:
                if self.clear_deadlock_interfere_vertex(tmp_solution, v, blocked, unoccupied_blocked, v_from, v_to):
                    committed_state = self.commit_state()
                    solution += tmp_solution
                    cleared.add(v)
                    unoccupied_blocked.add(v)
                else:
                    self.rollback_state(committed_state)
                    not_cleared.add(v)

        tmp_empty = copy.deepcopy(self._empty_vertices)
        tmp_empty = tmp_empty - cleared

        committed_state = self.commit_state()
        for v in not_cleared:
            tmp_solution = []
            if v in self._occupied_vertices:
                if not self.clear_deadlock_interfere_vertex(tmp_solution, v, blocked, unoccupied_blocked, v_from, v_to):
                    self.rollback_state(first_committed_state)
                    return False
                unoccupied_blocked.add(v)



        return True

    def clear_deadlock_interfere_vertex(self, solution, v, blocked, unoccupied_blocked, v_from, v_to):
        tmp_empty = set()
        agent = self._occupied_vertices[v_from]
        p_from = self._graph.get_vertex_position(v_from)
        p_to = self._graph.get_vertex_position(v_to)

        for eps in self._empty_vertices:
            if eps in unoccupied_blocked:
                continue
            if self.check_suspect_vertex(p_from, p_to, eps):
                continue
            tmp_empty.add(eps)

        tmp_graph = copy.deepcopy(self._graph)
        tmp_graph_deadlock_free = copy.deepcopy(self._graph_deadlock_free)

        for e in self._graph.get_edges():
            p1 = self._graph.get_vertex_position(e[0])
            p2 = self._graph.get_vertex_position(e[1])
            if self.check_suspect_vertex(p1, p2, v_to):
                tmp_graph.discard_edge(*e)
                tmp_graph_deadlock_free.discard_edge(*e)

        for eps in tmp_empty:
            # TODO
            # p_exists, p = shortest_path(tmp_graph_deadlock_free, v, eps, blocked)
            # if not p_exists:
            #     p_exists, p = shortest_path(tmp_graph, v, eps, blocked)
            #
            # if not p_exists:
            #     return False
            #
            # v_to = p.pop(0)
            # while v != v_to:
            #     v_from = p.pop(0)
            #     if v_from in self._occupied_vertices:
            #         agent = self._occupied_vertices[v_from]
            #         if not self.try_move_agent(solution, agent, v_from, v_to):
            #             return False
            #         v_to = v_from
            #     else:
            #         tmp_path = [v_to, v_from]
            #         tmp_v = p.pop(0)
            #         while True:
            #             if tmp_v in self._occupied_vertices:
            #                 break
            #             tmp_path.append(tmp_v)
            #             tmp_v = p.pop(0)
            #
            #         tmp_v_from = tmp_v
            #         tmp_v_to = tmp_path.pop()
            #         agent = self._occupied_vertices[tmp_v_from]
            #         while True:
            #             if not self.try_move_agent(solution, agent, tmp_v_from, tmp_v_to):
            #                 return False
            #             if tmp_v_to == v_to:
            #                 v_to = tmp_v
            #                 break
            #             tmp_v_from = tmp_v_to
            #             tmp_v_to = tmp_path.pop()


        return True

    def get_interfere_vertices(self, v_from, v_to):
        result = set()
        edge_len = self._graph.get_euclidian_distance(v_from, v_to)
        p_from = self._graph.get_vertex_position(v_from)
        p_to = self._graph.get_vertex_position(v_to)
        suspect_zone_size = edge_len + 2 * self._size
        suspect_vert = self._graph.get_vertices_in_zone(self._graph.get_vertex_position(v_from), suspect_zone_size)

        for v in suspect_vert:
            if v == v_from or v == v_to:
                continue
            if self.check_suspect_vertex(p_from, p_to, v):
                result.add(v)
        return result

    def check_suspect_vertex(self, edge_p1, edge_p2, suspect_v):
        suspect_p = self._graph.get_vertex_position(suspect_v)
        if dist_point_line_segment(edge_p1, edge_p2, suspect_p) < 2 * self._size:
            return True
        return False

    def check_move(self, agent, v_from, v_to):
        if self._agents_positions[agent] != v_from:
            print(self.debug_prefix, "Error: move from incorrect position!", agent, v_from, v_to)
            exit()
        if v_to in self._occupied_vertices:
            print(self.debug_prefix, "Error: move to occupied position!", agent, v_from, v_to)
            exit()
        if v_to not in self._graph.get_neighbours(v_from):
            print(self.debug_prefix, "Error: move to vertex without edge!", agent, v_from, v_to)
            exit()

        # if self.goals[agent] == v_from and v_from in self.reached_goals:
        #     print(self.debug_prefix,  "Alert! Agent ", agent, "moved from goal!")
        # if self.goals[agent] == v_to and v_to in self.reached_goals:
        #     print(self.debug_prefix,  "Alert! Agent ", agent, "moved back to goal!")

    def find_deadlock_edges(self):
        result = set()
        for e in self._graph.get_edges():
            if self.check_edge_on_deadlock(e):
                result.add(e)
        return result

    def check_edge_on_deadlock(self, edge):
        v_from, v_to = edge
        interfere_v = self.get_interfere_vertices(v_from, v_to)
        p_from = self._graph.get_vertex_position(v_from)
        p_to = self._graph.get_vertex_position(v_to)

        if len(interfere_v) == 0:
            return False
        print(edge, interfere_v)

        for v in interfere_v:
            p_from_2 = self._graph.get_vertex_position(v)
            for n in self._graph.get_neighbours(v):
                p_to_2 = self._graph.get_vertex_position(n)
                if n not in edge and\
                        not self.check_suspect_vertex(p_from_2, p_to_2, v_from) and \
                        not self.check_suspect_vertex(p_from_2, p_to_2, v_to) and \
                        not self.check_suspect_vertex(p_from, p_to, n):
                    break
            else:
                return True
        return False




