from .pathplanner import *
from utils.geom import dist_point_line_segment
from .graph import Graph

from typing import Dict, Set, List, Tuple, Optional
import copy


class PushAndRotateWithSizes:

    def __init__(self, graph, agents, starts, goals, size) -> None:
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

        self._debug_prefix = ""

        for e in self._deadlock_edges:
            self._graph_deadlock_free.discard_edge(*e)

        for agent, vert in starts.items():
            self._occupied_vertices.update({vert: agent})
            self._empty_vertices.discard(vert)

    def solve(self) -> Tuple[bool, Optional[List[Tuple[int, int, int]]]]:
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

    def plan_polygon(self, solution, agent) -> bool:
        # TODO
        return False

    def plan(self, solution, agent, queue) -> bool:
        committed_state = self.commit_state()
        graph_backup = copy.deepcopy(self._graph)
        graph_deadlock_free_backup = copy.deepcopy(self._graph_deadlock_free)
        queue_backup = copy.deepcopy(queue)

        while True:
            edge_removed = False
            tmp_solution = []
            self.rollback_state(committed_state)
            queue = copy.deepcopy(queue_backup)

            p_exists, p = self.find_path(self._graph_deadlock_free, self._graph, self._agents_positions[agent], self._goals[agent], set())
            if not p_exists:
                return False

            queue.append(p.pop())

            while self._agents_positions[agent] != self._goals[agent]:
                # print(p)
                v = p.pop()

                if v in queue:
                    graph_deadlock_free_backup, self._graph_deadlock_free = self._graph_deadlock_free, graph_deadlock_free_backup
                    graph_backup, self._graph = self._graph, graph_backup

                    rotate_res, queue = self.rotate(tmp_solution, queue, v)
                    if not rotate_res:
                        return False

                    graph_deadlock_free_backup, self._graph_deadlock_free = self._graph_deadlock_free, graph_deadlock_free_backup
                    graph_backup, self._graph = self._graph, graph_backup

                else:
                    pushed, base_push_works = self.push(tmp_solution, agent, v, self.successful_agents_positions())
                    if not base_push_works and not pushed:
                        if not self.swap(tmp_solution, agent, self._occupied_vertices[v]):
                            return False
                    elif base_push_works and not pushed:
                        edge_removed = True
                        print("remove edge after push failed", self._agents_positions[agent], v)
                        self._graph.discard_edge(self._agents_positions[agent], v)
                        self._graph_deadlock_free.discard_edge(self._agents_positions[agent], v)
                        break

                queue.append(v)
            
            if edge_removed:
                continue

            solution += tmp_solution
            self._graph = copy.deepcopy(graph_backup)
            self._graph_deadlock_free = copy.deepcopy(graph_deadlock_free_backup)
            self.agent_achieve_goal(agent)
            resolve_res = self.resolve(solution, queue)

            return resolve_res

    def push(self, solution, agent, v, blocked) -> Tuple[bool, bool]:
        print("(push) Start")
        if v in self._occupied_vertices:
            tmp_blocked = blocked | {self._agents_positions[agent]}

            cleared, base_push_works = self.clear_vertex(solution, v, tmp_blocked)
            if not cleared:
                return False, base_push_works

        return self.try_move_agent(solution, agent, self._agents_positions[agent], v, set()), True

    def clear_vertex(self, solution, v, blocked) -> Tuple[bool, bool]:
        print("(clear_vertex) Start", v)
        if v in blocked:
            print("(clear_vertex) Fail")
            return False, False

        committed_state = self.commit_state()
        tmp_graph = copy.deepcopy(self._graph)
        tmp_graph_deadlock_free = copy.deepcopy(self._graph_deadlock_free)

        base_push_works = False
        while True:
            tmp_solution = []
            self.rollback_state(committed_state)

            p_exists, p = self.find_path_to_empty_vertex(tmp_graph_deadlock_free, tmp_graph, v, self._empty_vertices, blocked)
            if not p_exists:
                print("(clear_vertex) Fail")
                return False, base_push_works

            base_push_works = True

            pushed, blocked_edge = self.push_forward_path(tmp_solution, p, v, set())
            if pushed:
                solution += tmp_solution
                print("(clear_vertex) Succ")
                return True, base_push_works
            else:
                tmp_graph.discard_edge(*blocked_edge)
                tmp_graph_deadlock_free.discard_edge(*blocked_edge)

    def swap(self, solution, agent_1, agent_2) -> bool:
        print("(swap) Start")
        s = self._graph.get_vertices_degree_geq_3()
        committed_state = self.commit_state()

        for v in s:
            tmp_solution = []
            self.rollback_state(committed_state)
            if self.multipush(tmp_solution, agent_1, agent_2, v):
                if self.clear(tmp_solution, agent_1, agent_2, v):
                    print("Clear succ")
                    tmp_solution_2 = []
                    tmp_solution_2 += tmp_solution
                    if self.exchange(tmp_solution_2, agent_1, agent_2, v):
                        self.reverse(tmp_solution_2, tmp_solution, agent_1, agent_2)
                        solution += tmp_solution_2
                    # print("(swap) End")
                        return True
        print("(swap) fail")
        return False

    def multipush(self, solution, agent_1, agent_2, v) -> bool:
        print("(multipush) Start", agent_1, agent_2, v)

        tmp_graph_deadlock_free = copy.deepcopy(self._graph_deadlock_free)
        tmp_graph = copy.deepcopy(self._graph)
        committed_state = self.commit_state()
        tmp_solution = []

        while True:
            self.rollback_state(committed_state)
            tmp_solution = []

            p_exists, p = self.find_path(tmp_graph_deadlock_free, tmp_graph, self._agents_positions[agent_1], v, set())
    
            if not p_exists:
                print("(multipush) End path not found(f)", agent_1, agent_2, v)
                return False

            if (self._agents_positions[agent_1], self._agents_positions[agent_2]) not in tmp_graph.get_edges() and \
                    (self._agents_positions[agent_2], self._agents_positions[agent_1]) not in tmp_graph.get_edges():
                print("(multipush) End (f)", agent_1, agent_2, v)
                return False

            if len(p) < 2:
                print("(multipush) End (t)", agent_1, agent_2, v)
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
                    cleared, _ = self.clear_vertex(tmp_solution, waypoint, blocked)
                    if not cleared:
                        tmp_graph.discard_edge(v_r, waypoint)
                        tmp_graph_deadlock_free.discard_edge(v_r, waypoint)
                        break

                if not self.try_move_agent(tmp_solution, r, v_r, waypoint, set()):
                    tmp_graph.discard_edge(v_r, waypoint)
                    tmp_graph_deadlock_free.discard_edge(v_r, waypoint)
                    break
                if not self.try_move_agent(tmp_solution, s, v_s, v_r, set()):
                    print("second agent multipush Fail")
                    tmp_graph.discard_edge(v_s, v_r)
                    tmp_graph_deadlock_free.discard_edge(v_s, v_r)
                    break
            else:
                break

        solution += tmp_solution
        print("(multipush) End (t)", agent_1,  self._agents_positions[agent_1], agent_2, self._agents_positions[agent_2])
        return True

    def clear(self, solution, agent_1, agent_2, v) -> bool:
        print("(clear) Start", agent_1, agent_2, v)
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

        print("(clear) case 1")
        # print(self._agents_positions)
        for n in neighbours:
            if (n in empty_neighbours) or (n == v1):
                continue
            if self.clear_vertex(solution, n, empty_neighbours | {v, v1})[0]:
                if len(empty_neighbours) > 0:
                    return True
                empty_neighbours.add(n)

        if len(empty_neighbours) == 0:
            return False

        print("(clear) case 2")
        print(self._agents_positions)
        eps = empty_neighbours.pop()
        committed_state = self.commit_state()

        for n in neighbours:
            if (n == eps) or (n == v1):
                continue
            tmp_solution = []
            self.rollback_state(committed_state)
            if self.clear_vertex(tmp_solution, n, {v, v1})[0]:
                if self.clear_vertex(tmp_solution, eps, {v, v1, n})[0]:
                    solution += tmp_solution
                    return True
                break

        print(self._agents_positions)
        print("(clear) case 3")

        # print(self._agents_positions)
        for n in neighbours:
            print("(clear) n:", n)
            if (n == eps) or (n == v1):
                continue
            tmp_solution = []
            self.rollback_state(committed_state)
            if not self.try_move_agent(tmp_solution, r, self._agents_positions[r], eps, set()) or \
                    not self.try_move_agent(tmp_solution, s, self._agents_positions[s], v, set()):
                continue

            if self.clear_vertex(tmp_solution, n, {v, eps})[0]:
                if self.clear_vertex(tmp_solution, v1, {v, eps, n})[0]:
                    solution += tmp_solution
                    return True
                break

        self.rollback_state(committed_state)

        print(self._agents_positions)
        if not self.clear_vertex(solution, v1, {v})[0]:
            return False


        if not self.try_move_agent(solution, r, self._agents_positions[r], v1, set()):
            return False

        if not self.clear_vertex(solution, eps, {v, v1, self._agents_positions[s]})[0]:
            return False

        n = neighbours.pop()
        while True:
            if (n != v1) and (n != eps):
                break
            n = neighbours.pop()

        t = self._occupied_vertices[n]

        if not self.try_move_agent(solution, t, n, v, set()):
            return False
        if not self.try_move_agent(solution, t, v, eps, set()):
            return False
        if not self.try_move_agent(solution, r, self._agents_positions[r], v, set()):
            return False
        if not self.try_move_agent(solution, s, self._agents_positions[s], v1, set()):
            return False

        return self.clear_vertex(solution, eps, {v, v1, n})[0]

    def exchange(self, solution, agent_1, agent_2, v) -> bool:
        print("(exchange) Start")
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
        if not self.try_move_agent(solution, r, v, v1, set()):
            return False
        if not self.try_move_agent(solution, s, v_s, v, set()):
            return False
        if not self.try_move_agent(solution, s, v, v2, set()):
            return False
        if not self.try_move_agent(solution, r, v1, v, set()):
            return False
        if not self.try_move_agent(solution, r, v, v_s, set()):
            return False
        if not self.try_move_agent(solution, s, v2, v, set()):
            return False
        return True

    def circular_buffer_index(self, ind, buff_len) -> int:
        if ind < 0:
            return -(abs(ind) % buff_len)
        else:
            return abs(ind) % buff_len

    def rotate(self, solution, queue, v) -> Tuple[bool, Optional[List[int]]]:
        print("(rotate) Start")
        print(queue)
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
                        if not self.try_move_agent(solution, self._occupied_vertices[move_from], move_from, move_to, set()):
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
                if not self.try_move_agent(solution, r2, v2, v1, set()):
                    return False, None

                if not self.swap(solution, r, r2):
                    return False, None

                i_move_from = self.circular_buffer_index(ind - 2, len(c))
                i_move_to = self.circular_buffer_index(ind - 1, len(c))

                while True:
                    move_from = c[i_move_from]
                    move_to = c[i_move_to]
                    if not self.try_move_agent(solution, self._occupied_vertices[move_from], move_from, move_to, set()):
                        return False, None
                    i_move_to = self.circular_buffer_index(i_move_from, len(c))
                    i_move_from = self.circular_buffer_index(i_move_from - 1, len(c))

                    if c[i_move_from] == v2:
                        break

                self.reverse(solution, tmp_solution, r, r2)
                return True, queue
        return False, None

    def resolve(self, solution, queue) -> bool:

        # print("(resolve) Start")

        while len(queue) > 0:
            v = queue[-1]
            # print(v)
            if v in self._occupied_vertices:
                r = self._occupied_vertices[v]
                if r in self._successful_agents and self._agents_positions[r] != self._goals[r]:
                    committed_state = self.commit_state()
                    tmp_solution = []
                    pushed, base_push_worked = self.push(tmp_solution, r, self._goals[r], self.successful_agents_positions())
                    if not pushed:
                        self.rollback_state(committed_state)
                        if not base_push_worked:
                            s = self._occupied_vertices[self._goals[r]]
                            return self.plan(solution, s, queue)
                        else:
                            queue.pop()
                            self._reached_goals.discard(self._goals[r])
                            self._successful_agents.discard(r)
                            return self.plan(solution, r, queue)
                    solution += tmp_solution
            queue.pop()
        # print("(resolve) End")
        return True

    def reverse(self, solution, tail, agent_1=None, agent_2=None) -> None:
        if (len(tail)):
            print("(reverse)")
        for move in reversed(tail):
            if agent_1 is not None and move[0] == agent_1:
                self.move_agent(solution, agent_2, move[2], move[1])
            elif agent_2 is not None and move[0] == agent_2:
                self.move_agent(solution, agent_1, move[2], move[1])
            else:
                self.move_agent(solution, move[0], move[2], move[1])
        if (len(tail)):
            print("(reverse end)")

    def move_agent(self, solution, agent, v_from, v_to) -> None:
        print("\t(move) Agent:", agent, "from", v_from, "to", v_to)
        self.check_move_tech(agent, v_from, v_to)

        if not check_collision(self._graph, v_from, v_to, self._size, self._occupied_vertices):
            print("Error: move to vertex with collision!", agent, v_from, v_to)
            exit()

        self._empty_vertices.add(v_from)
        self._empty_vertices.remove(v_to)
        self._occupied_vertices.update({v_to: agent})
        self._occupied_vertices.pop(v_from)
        self._agents_positions[agent] = v_to
        solution.append((agent, v_from, v_to))

    def agent_achieve_goal(self, agent) -> None:
        self._reached_goals.add(self._goals[agent])
        self._successful_agents.add(agent)

    def commit_state(self) -> Tuple[Set[int], Dict[int, int], Dict[int, int]]:
        tmp_empty = copy.deepcopy(self._empty_vertices)
        tmp_occupied = copy.deepcopy(self._occupied_vertices)
        tmp_pos = copy.deepcopy(self._agents_positions)

        return (tmp_empty, tmp_occupied, tmp_pos)

    def rollback_state(self, state) -> None:
        self._empty_vertices = copy.deepcopy(state[0])
        self._occupied_vertices = copy.deepcopy(state[1])
        self._agents_positions = copy.deepcopy(state[2])

    def successful_agents_positions(self) -> Set[int]:
        return set([self._agents_positions[a] for a in self._successful_agents])

    def try_move_agent(self, solution, agent, v_from, v_to, blocked) -> bool:
        print("\t(try move) Agent:", agent, "from", v_from, "to", v_to)
        self.check_move_tech(agent, v_from, v_to)
        local_solution = []       
        cleared, sol_rev = self.clear_edge(local_solution, agent, v_from, v_to, blocked)
        
        if not cleared:
            print("\t(try move end f) Agent:", agent, "from", v_from, "to", v_to)
            return False
        solution += local_solution
        self.move_agent(solution, agent, v_from, v_to)
        self.reverse(solution, sol_rev)
        print("\t(try move end t) Agent:", agent, "from", v_from, "to", v_to)
        return True

    def clear_edge(self, solution, agent, v_from, v_to, blocked) -> Tuple[bool, Optional[List[Tuple[int, int, int]]]]:
        
        cleared = set()
        not_cleared = set()

        interfere_v = self.get_interfere_vertices(v_from, v_to)
        # blocked |= {v_to}
        cleared = interfere_v & self._empty_vertices
        initial_state = self.commit_state()

        committed_state = self.commit_state()

        solution_reverse = []
        for v in interfere_v:
            local_solution = []
            if v in self._occupied_vertices:
                if self.clear_interfere_vertex(local_solution, v, blocked | {v_to}, cleared, v_from, v_to):
                    committed_state = self.commit_state()
                    solution += local_solution
                    solution_reverse += self.remove_agent_moves_from_solution(local_solution, agent)
                    cleared.add(v)
                else:
                    self.rollback_state(committed_state)
                    not_cleared.add(v)


        committed_state = self.commit_state()
        for v in not_cleared:
            local_solution = []
            if v in self._occupied_vertices:
                is_cleared, before_agent_solution, agent_solution, after_agent_solution = self.clear_deadlock_interfere_vertex(local_solution, v, blocked, cleared, v_from, v_to)
                
                if not is_cleared:
                    self.rollback_state(initial_state)

                    return False, None

                cleared.add(v)
                solution += local_solution
                print("after", after_agent_solution)
                solution_reverse += self.remove_agent_moves_from_solution(before_agent_solution + after_agent_solution, agent)
        print(solution_reverse)
        return True, solution_reverse

    def remove_agent_moves_from_solution(self, solution, agent):
        new_solution = []
        for step in solution:
            if step[0] == agent:
                continue
            new_solution.append(step)
        return new_solution
    
    def clear_interfere_vertex(self, solution, v, blocked, unoccupied_blocked, v_from, v_to) -> bool:
        empty_goals = set()
        p_from = self._graph.get_vertex_position(v_from)
        p_to = self._graph.get_vertex_position(v_to)
        for eps in self._empty_vertices:
            if eps in unoccupied_blocked:
                continue
            if self.check_suspect_vertex(p_from, p_to, eps):
                continue
            empty_goals.add(eps)

        graph_backup = copy.deepcopy(self._graph)
        graph_deadlock_free_backup = copy.deepcopy(self._graph_deadlock_free)

        for e in self._graph.get_edges():
            p1 = self._graph.get_vertex_position(e[0])
            p2 = self._graph.get_vertex_position(e[1])
            if self.check_suspect_vertex(p1, p2, v_to):
                self._graph.discard_edge(*e)
                self._graph_deadlock_free.discard_edge(*e)

        commited_state = self.commit_state()

        for eps in empty_goals:
            while True:
                p_exists, p = self.find_path(self._graph_deadlock_free, self._graph, v, eps, blocked | {v_from})
                if not p_exists:
                    break
                local_solution = []

                pushed, fail_edge = self.push_forward_path(local_solution, p, v, blocked)
                if pushed:
                    self._graph = graph_backup
                    self._graph_deadlock_free = graph_deadlock_free_backup
                    solution += local_solution
                    return True
                
                self._graph.discard_edge(*fail_edge)
                self._graph_deadlock_free.discard_edge(*fail_edge)
                self.rollback_state(commited_state)
        
        self._graph = graph_backup
        self._graph_deadlock_free = graph_deadlock_free_backup
        return False

    def clear_deadlock_interfere_vertex(self, solution, v, blocked, unoccupied_blocked, v_from, v_to) -> Tuple[bool, Optional[List[Tuple[int, int, int]]], Optional[List[Tuple[int, int, int]]], Optional[List[Tuple[int, int, int]]]]:   
        print("clear_deadlock_interfere_vertex")
        agent = self._occupied_vertices[v_from]
        interfere_agent = self._occupied_vertices[v]
        graph_backup = copy.deepcopy(self._graph)
        graph_deadlock_free_backup = copy.deepcopy(self._graph_deadlock_free)

        blocked_edges = set()
        for e in self._graph.get_edges():
                p1 = self._graph.get_vertex_position(e[0])
                p2 = self._graph.get_vertex_position(e[1])
                if self.check_suspect_vertex(p1, p2, v_to):
                    blocked_edges.add(e)

        neighbours = self._graph.get_neighbours(v_from) - ({v, v_to} | blocked)
        committed_state = self.commit_state()
        
        for n in neighbours:
            self._graph = copy.deepcopy(graph_backup)
            self._graph_deadlock_free = copy.deepcopy(graph_deadlock_free_backup)
            
            for e in blocked_edges:
                self._graph.discard_edge(*e)
                self._graph_deadlock_free.discard_edge(*e)
            
            self.rollback_state(committed_state)
            agent_solution = []
            local_solution = []
            agent_empty_goals = self._empty_vertices - (unoccupied_blocked | {v_to})
            path_found = True
            pushed = True
            

            if n not in self._empty_vertices:
                path_found = False
                pushed = False
                for eps in agent_empty_goals:
                    self.rollback_state(committed_state)
                    agent_solution = []
                    local_solution = []

                    path_found = False
                    pushed = False

                    while True:
                        local_solution = []
                        p_exists, p = self.find_path(self._graph_deadlock_free, self._graph, n, eps, blocked | {v_from, v_to, v})
                        if not p_exists:
                            path_found = False
                            break

                        path_found = True
                        # print([self._occupied_vertices.get(vvv) for vvv in p])
                        # print(n in self._empty_vertices)
                        pushed, fail_edge = self.push_forward_path(local_solution, p, n, blocked | {v_to})
                        if pushed:
                            break
                        self._graph.discard_edge(*fail_edge)
                        self._graph_deadlock_free.discard_edge(*fail_edge)
                        self.rollback_state(committed_state)
                        
                    if not path_found:
                        continue
                    if pushed:
                        break
            
            # print(path_found, pushed)

            print("agent begin")

            graph_backup_tmp = copy.deepcopy(self._graph)
            graph_deadlock_free_backup_tmp = copy.deepcopy(self._graph_deadlock_free)
            
            self._graph = copy.deepcopy(graph_backup)
            self._graph_deadlock_free = copy.deepcopy(graph_deadlock_free_backup)
            self._graph.discard_edge(v_from, v_to)
            self._graph_deadlock_free.discard_edge(v_from, v_to)
            
            if  not pushed or not self.try_move_agent(agent_solution, agent, v_from, n, blocked ):
                self.rollback_state(committed_state)
                continue

            self._graph = copy.deepcopy(graph_backup_tmp)
            self._graph_deadlock_free = copy.deepcopy(graph_deadlock_free_backup_tmp)
            print("agent end")

            for e in blocked_edges:
                self._graph.discard_edge(*e)
                self._graph_deadlock_free.discard_edge(*e)

            empty_goals = self._empty_vertices - \
                    (self.get_all_positions_in_solution(agent_solution) | self.get_interfere_vertices(v_from, n) | unoccupied_blocked)

            committed_state_2 = self.commit_state()
            local_solution_part_2 = []
            graph_backup_2 = copy.deepcopy(self._graph)
            graph_deadlock_free_backup_2 = copy.deepcopy(self._graph_deadlock_free)
            agent_solution_positions = self.get_participants_current_positions(agent_solution)
            print("agent sol pos", agent_solution_positions)
            for eps_2 in empty_goals:
                local_solution_part_2 = []
                self.rollback_state(committed_state_2)
                path_found = False
                pushed = False
                self._graph = copy.deepcopy(graph_backup_2)
                self._graph_deadlock_free = copy.deepcopy(graph_deadlock_free_backup_2)

                while True:
                    local_solution_part_2 = []
                    p_exists, p = self.find_path(self._graph_deadlock_free, self._graph, v, eps_2, blocked | agent_solution_positions | {v_to})
                    if not p_exists:
                        path_found = False
                        break
                    path_found = True

                    print("aaaaaaaa", local_solution_part_2)
                    pushed, fail_edge = self.push_forward_path(local_solution_part_2, p, v, blocked | {v_to})
                    if pushed:
                        print("bbbbbbbb", local_solution_part_2)
                        break

                    self._graph.discard_edge(*fail_edge)
                    self._graph_deadlock_free.discard_edge(*fail_edge)
                    self.rollback_state(committed_state_2)
                
                if not path_found:
                    continue

                if pushed:
                    self._graph = graph_backup
                    self._graph_deadlock_free = graph_deadlock_free_backup
                    solution += local_solution
                    solution += agent_solution
                    solution += local_solution_part_2
                    print(agent_solution)
                    self.reverse(solution, self.remove_agent_moves_from_solution(agent_solution, interfere_agent))
                    print("clear_deadlock_interfere_vertex end t")
                    return True, local_solution, agent_solution, local_solution_part_2
                
            # self._graph = graph_backup
            # self._graph_deadlock_free = graph_deadlock_free_backup
            # return False, None, None, None

        self._graph = graph_backup
        self._graph_deadlock_free = graph_deadlock_free_backup
        print("clear_deadlock_interfere_vertex end f")
        return False, None, None, None

    def get_participants_current_positions(self, solution):
        positions = set()
        for step in solution:
            agent = step[0]
            positions.add(self._agents_positions[agent])
        return positions

    def get_all_positions_in_solution(self, solution):
        positions = set()
        for step in solution:
            pos1 = step[1]
            pos2 = step[2]
            positions.add(pos1)
            positions.add(pos2)
        return positions

    def push_forward_path(self, solution, p, v, blocked) -> Tuple[bool, Optional[Tuple[int, int]]]:
        print("push path", p)
        v_to = p.pop(0)
        while v != v_to:
            v_from = p.pop(0)
            if v_from in self._occupied_vertices:
                agent = self._occupied_vertices[v_from]
                if not self.try_move_agent(solution, agent, v_from, v_to, blocked):
                    # print("push path fail")
                    return False, (v_from, v_to)
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
                    if not self.try_move_agent(solution, agent, tmp_v_from, tmp_v_to, blocked):
                        # print("push path fail")
                        return False, (tmp_v_from, tmp_v_to)
                    if tmp_v_to == v_to:
                        v_to = tmp_v
                        break
                    tmp_v_from = tmp_v_to
                    tmp_v_to = tmp_path.pop()
        # print("push path end")
        return True, None

    def split_positions_from_solution(self, solution, agent) -> Tuple[Set[int], Set[int], Set[int]]:
        positions = set()
        other = set()
        interfere_empty = set()
        for a, f, t in solution:
            if a == agent:
                positions.add(f)
                positions.add(t)
                interfere_empty |= (self.get_interfere_vertices(f, t) & self._empty_vertices)
            else:
                other.add(f)
                other.add(t)

        return positions, interfere_empty, other

    def get_interfere_vertices(self, v_from, v_to) -> Set[int]:
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

    def check_suspect_vertex(self, edge_p1, edge_p2, suspect_v) -> bool:
        suspect_p = self._graph.get_vertex_position(suspect_v)

        if dist_point_line_segment(edge_p1, edge_p2, suspect_p) < 2 * self._size:
            return True
        return False

    def check_move_tech(self, agent, v_from, v_to) -> None:
        if self._agents_positions[agent] != v_from:
            print( "Error: move from incorrect position! a, from, to", agent, v_from, v_to)
            exit()
        if v_to in self._occupied_vertices:
            print("Error: move to occupied position! a, from, to", agent, v_from, v_to)
            exit()
        if v_to not in self._graph.get_neighbours(v_from):
            print("Error: move to vertex without edge! a, from, to", agent, v_from, v_to)
            exit()

    def find_deadlock_edges(self) -> Set[Tuple[int, int]]:
        result = set()
        for e in self._graph.get_edges():
            if self.check_edge_on_deadlock(e):
                result.add(e)
        return result

    def check_edge_on_deadlock(self, edge) -> bool:
        v_from, v_to = edge
        interfere_v = self.get_interfere_vertices(v_from, v_to)
        p_from = self._graph.get_vertex_position(v_from)
        p_to = self._graph.get_vertex_position(v_to)

        if len(interfere_v) == 0:
            return False
        # print(edge, interfere_v)

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

    def find_path(self, graph_deadlock_free, graph, start, goal, blocked) -> Tuple[bool, Optional[List[int]]]:
        p_exists, p = shortest_path(graph_deadlock_free, start, goal, blocked)
        if not p_exists:
            p_exists, p = shortest_path(graph, start, goal, blocked)
        return p_exists, p

    def find_path_to_empty_vertex(self, graph_deadlock_free, graph, start, empty, blocked) -> Tuple[bool, Optional[List[int]]]:
        p_exists, p = path_to_closest_empty_vertex(graph_deadlock_free, start, empty, blocked)
        if not p_exists:
            p_exists, p = path_to_closest_empty_vertex(graph, start, empty, blocked)
        return p_exists, p








   # def clear_interfere_vertex(self, solution, v, blocked, unoccupied_blocked, v_from, v_to) -> bool:
    #     print("(clear_interfere_vertex) from, to, interf", v_from, v_to, v)
    #     tmp_empty = set()
    #     p_from = self._graph.get_vertex_position(v_from)
    #     p_to = self._graph.get_vertex_position(v_to)

    #     for eps in self._empty_vertices:
    #         if eps in unoccupied_blocked:
    #             continue
    #         if self.check_suspect_vertex(p_from, p_to, eps):
    #             continue
    #         tmp_empty.add(eps)

    #     tmp_graph = copy.deepcopy(self._graph)
    #     tmp_graph_deadlock_free = copy.deepcopy(self._graph_deadlock_free)

    #     for e in self._graph.get_edges():
    #         p1 = self._graph.get_vertex_position(e[0])
    #         p2 = self._graph.get_vertex_position(e[1])
    #         if self.check_suspect_vertex(p1, p2, v_from) or self.check_suspect_vertex(p1, p2, v_to):
    #             tmp_graph.discard_edge(*e)
    #             tmp_graph_deadlock_free.discard_edge(*e)

    #     commited_state = self.commit_state()
    #     for eps in tmp_empty:
    #         p_exists, p = self.find_path(tmp_graph_deadlock_free, tmp_graph, v, eps, blocked | {v})
    #         print("goal", eps, "path", p)
    #         if not p_exists:
    #             continue
    #         tmp_solution = []

    #         if self.push_forward_path(tmp_solution, p, v, blocked)[0]:
    #             solution += tmp_solution
    #             return True
    #         self.rollback_state(commited_state)
            
    #     return False







# def clear_deadlock_interfere_vertex(self, solution, v, blocked, unoccupied_blocked, v_from, v_to) -> Tuple[bool, Optional[List[Tuple[int, int, int]]], Optional[List[Tuple[int, int, int]]]]:   
#         tmp_empty = set()
#         agent = self._occupied_vertices[v_from]
#         p_from = self._graph.get_vertex_position(v_from)
#         p_to = self._graph.get_vertex_position(v_to)

#         tmp_empty = copy.deepcopy(self._empty_vertices)


#         tmp_graph = copy.deepcopy(self._graph)
#         tmp_graph_deadlock_free = copy.deepcopy(self._graph_deadlock_free)

#         for e in self._graph.get_edges():
#             p1 = self._graph.get_vertex_position(e[0])
#             p2 = self._graph.get_vertex_position(e[1])
#             if self.check_suspect_vertex(p1, p2, v_to):
#                 tmp_graph.discard_edge(*e)
#                 tmp_graph_deadlock_free.discard_edge(*e)

#         committed_state = self.commit_state()

#         for eps in tmp_empty:

#             p_exists, p = self.find_path(tmp_graph_deadlock_free, tmp_graph, v_from, eps, blocked | {v})

#             if not p_exists: # or (len(p) > 2 and eps in unoccupied_blocked):
#                 print("(clear_deadlock_interfere_vertex) empty goal path not found. empty goal:", eps)
#                 print(blocked)
#                 continue

#             agent_solution = []
#             other_solution = []

#             # Error was here! {v_from, v_to}
#             rev_excluded_agents = set()
#             for pos in p:
#                 if pos in self._occupied_vertices:
#                     rev_excluded_agents.add(self._occupied_vertices[pos])
               

#             if not self.push_forward_path(agent_solution, p, v_from, blocked)[0]:
#                 self.rollback_state(committed_state)
#                 continue

#             agent_pos, interfere_pos, other_pos = self.split_positions_from_solution(agent_solution, agent)

#             tmp_empty_2 = set()

#             for eps_2 in self._empty_vertices:

#                 if (eps_2 in unoccupied_blocked) or (eps_2 in agent_pos) or \
#                         (eps_2 in interfere_pos) or (eps_2 in other_pos):
#                     continue
#                 if self.check_suspect_vertex(p_from, p_to, eps_2):
#                     continue
#                 tmp_empty_2.add(eps_2)

#             tmp_blocked = blocked | (other_pos - self._empty_vertices)
#             tmp_blocked.add(self._agents_positions[agent])
#             tmp_blocked.discard(v_from)
#             tmp_graph_2 = copy.deepcopy(tmp_graph)
#             tmp_graph_deadlock_free_2 = copy.deepcopy(tmp_graph_deadlock_free)


#             p_exists, p = self.find_path_to_empty_vertex(tmp_graph_deadlock_free_2, tmp_graph_2, v, tmp_empty_2, tmp_blocked)
#             if not p_exists:
#                 self.rollback_state(committed_state)
#                 continue

#             if not self.push_forward_path(other_solution, p, v, blocked)[0]:
#                 self.rollback_state(committed_state)
#                 continue

#             solution += agent_solution
#             solution += other_solution
            
#             other_solution_aft_excl = []
#             for step in other_solution:
#                 if step[0] not in rev_excluded_agents:
#                     other_solution_aft_excl.append(step)

#             return True, agent_solution, other_solution_aft_excl

#         print("(clear_deadlock_interfere_vertex) fail from, to, iner", v_from, v_to, v)
#         return False, None, None






















    #  def clear_deadlock_interfere_vertex(self, solution, v, blocked, unoccupied_blocked, v_from, v_to) -> Tuple[bool, Optional[List[Tuple[int, int, int]]], Optional[List[Tuple[int, int, int]]]]:

    #     # TODO all cases
    #     step_back_goals = set()
    #     agent = self._occupied_vertices[v_from]
    #     p_from = self._graph.get_vertex_position(v_from)
    #     p_to = self._graph.get_vertex_position(v_to)

    #     step_back_goals = copy.deepcopy(self._empty_vertices)

    #     graph_backup = copy.deepcopy(self._graph)
    #     graph_deadlock_free_backup = copy.deepcopy(self._graph_deadlock_free)

    #     for e in self._graph.get_edges():
    #         p1 = self._graph.get_vertex_position(e[0])
    #         p2 = self._graph.get_vertex_position(e[1])
    #         if self.check_suspect_vertex(p1, p2, v_to):
    #             self._graph.discard_edge(*e)
    #             self._graph_deadlock_free.discard_edge(*e)

    #     committed_state = self.commit_state()
    #     current_solution = []
    #     for eps in step_back_goals:
            
    #         next_step_back_goal = False
    #         while True:
    #             p_exists, p = self.find_path(self._graph_deadlock_free, self._graph, v, eps, blocked | {v})
    #             if not p_exists:
    #                 next_step_back_goal = True
    #                 break
                
    #             other_path = p
    #             agent_path = [other_path.pop()]
        
    #             while True:
    #                 v_to = other_path.pop()
    #                 if v_to in unoccupied_blocked:
    #                     agent_path.insert(0, v_to)
    #                 else:
    #                     break
    #             agent_path.insert(0, other_path.pop())

    #             current_solution = []
    #             pushed, fail_edge = self.push_forward_path(current_solution, other_path, v, blocked)
    #             if pushed:
    #                 self._graph = graph_backup
    #                 self._graph_deadlock_free = graph_deadlock_free_backup
    #                 break
                
    #             self._graph.discard_edge(*fail_edge)
    #             self._graph_deadlock_free.discard_edge(*fail_edge)
    #             self.rollback_state(committed_state)


    #             current_solution = []
    #             pushed, fail_edge = self.push_forward_path(current_solution, other_path, v, blocked)
    #             if pushed:
    #                 self._graph = graph_backup
    #                 self._graph_deadlock_free = graph_deadlock_free_backup
    #                 break
                
    #             self._graph.discard_edge(*fail_edge)
    #             self._graph_deadlock_free.discard_edge(*fail_edge)
    #             self.rollback_state(committed_state)



    #         if next_step_back_goal:
    #             continue


    #         empty_goals = set()
    #         for eps_2 in self._empty_vertices:

    #             if (eps_2 in unoccupied_blocked) or (eps_2 in agent_pos) or \
    #                     (eps_2 in interfere_pos) or (eps_2 in other_pos):
    #                 continue
    #             if self.check_suspect_vertex(p_from, p_to, eps_2):
    #                 continue
    #             empty_goals.add(eps_2)




    #         # agent_solution = []
    #         # other_solution = []

    #         # rev_excluded_agents = set()
    #         # for pos in p:
    #         #     if pos in self._occupied_vertices:
    #         #         rev_excluded_agents.add(self._occupied_vertices[pos])
               

    #         # if not self.push_forward_path(agent_solution, p, v_from, blocked)[0]:
    #         #     self.rollback_state(committed_state)
    #         #     continue

    #         # agent_pos, interfere_pos, other_pos = self.split_positions_from_solution(agent_solution, agent)

            

            

    #         tmp_blocked = blocked | (other_pos - self._empty_vertices)
    #         tmp_blocked.add(self._agents_positions[agent])
    #         tmp_blocked.discard(v_from)
    #         tmp_graph_2 = copy.deepcopy(tmp_graph)
    #         tmp_graph_deadlock_free_2 = copy.deepcopy(tmp_graph_deadlock_free)


    #         p_exists, p = self.find_path_to_empty_vertex(tmp_graph_deadlock_free_2, tmp_graph_2, v, tmp_empty_2, tmp_blocked)
    #         if not p_exists:
    #             self.rollback_state(committed_state)
    #             continue

    #         if not self.push_forward_path(other_solution, p, v, blocked)[0]:
    #             self.rollback_state(committed_state)
    #             continue

    #         solution += agent_solution
    #         solution += other_solution
            
    #         other_solution_aft_excl = []
    #         for step in other_solution:
    #             if step[0] not in rev_excluded_agents:
    #                 other_solution_aft_excl.append(step)

            

    #         return True, agent_solution, other_solution_aft_excl

    #     print("(clear_deadlock_interfere_vertex) fail from, to, iner", v_from, v_to, v)
    #     return False, None, None



    #  def clear_edge(self, solution, agent, v_from, v_to, blocked) -> Tuple[bool, Optional[List[Tuple[int, int, int]]], Optional[List[Tuple[int, int, int]]], Optional[List[Tuple[int, int, int]]]]:
    #     print(self._debug_prefix, "(clear_deadlock_edge) Start. from to", v_from, v_to)
    #     self._debug_prefix += " "
    #     cleared = set()
    #     not_cleared = set()

    #     interfere_v = self.get_interfere_vertices(v_from, v_to)
    #     blocked |= {v_to}     
    #     for v in interfere_v:
    #         if v not in self._occupied_vertices:
    #             cleared.add(v)

    #     first_committed_state = self.commit_state()

    #     committed_state = self.commit_state()
    #     solution_1 = []
    #     for v in interfere_v:
    #         tmp_solution = []
    #         if v in self._occupied_vertices:
    #             if self.clear_interfere_vertex(tmp_solution, v, blocked, cleared, v_from, v_to):
    #                 committed_state = self.commit_state()
    #                 solution_1 += tmp_solution
    #                 cleared.add(v)
    #             else:
    #                 self.rollback_state(committed_state)
    #                 not_cleared.add(v)

    #     solution_2 = []
    #     solution_3 = []
    #     committed_state = self.commit_state()
    #     for v in not_cleared:
    #         tmp_solution = []
    #         if v in self._occupied_vertices:
    #             is_cleared, agent_solution, other_solution = self.clear_deadlock_interfere_vertex(tmp_solution, v, blocked, cleared, v_from, v_to)
    #             if not is_cleared:
    #                 self.rollback_state(first_committed_state)
    #                 self._debug_prefix = self._debug_prefix[:-1]
    #                 return False, None, None, None
    #             self.reverse(tmp_solution, agent_solution)
    #             cleared.add(v)
    #             solution_2 += tmp_solution
    #             solution_3 += other_solution
    #     solution += solution_1
    #     solution += solution_2
                    
    #     solution_1 = self.remove_agent_moves_from_solution(solution_1, agent)

    #     self._debug_prefix = self._debug_prefix[:-1]
    #     return True, solution_1, solution_2, solution_3





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