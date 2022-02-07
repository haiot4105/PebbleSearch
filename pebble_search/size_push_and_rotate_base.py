# from . import pathplanner

from .pathplanner import shortest_path
from .pathplanner import path_to_closest_empty_vertex
from utils.geom import dist_point_line_segment

import copy

class SizePushAndRotateBase:
    
    def __init__(self, graph, agents, starts, goals, size):
        self.graph = graph
        self.agents = agents
        self.starts = starts
        self.goals = goals
        self._size: float = size

        self.agents_positions = copy.deepcopy(starts)
        self.reached_goals = set() 
        self.successful_agents = set()
        self.empty_vertices = copy.deepcopy(graph.vertices)
        self.occupied_vertices = dict()

        for agent, vert in starts.items():
            self.occupied_vertices.update({vert : agent})
            self.empty_vertices.discard(vert)

        print("empty:", self.empty_vertices)

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
        print("(plan) Start")
        p_exists, p = shortest_path(self.graph, self.agents_positions[agent], self.goals[agent], {})
        print(p)
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
                    if not self.swap(solution, agent, self.occupied_vertices[v]):
                        return False

            queue.append(v)
        print(queue)
        self.agent_achive_goal(agent)
        resolve_res = self.resolve(solution, queue)
        print("(plan) End")
        return resolve_res

    def push(self, solution, agent, v, blocked):
        print("(push) Start")
        if v in self.occupied_vertices:
            tmp_blocked = blocked | {self.agents_positions[agent]}
            
            if not self.clear_vertex(solution, v, tmp_blocked):
                return False

        self.move_agent(solution, agent, self.agents_positions[agent], v)
        return True

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
            self.move_agent(solution, r1, v1, v2)
            v2 = v1
        return True

    def swap(self, solution, agent_1, agent_2):
        print("(swap) Start", agent_1, agent_2)

        S = self.graph.get_vertices_degree_geq_3()
        commited_state = self.commit_state()

        for v in S:
            tmp_solution = []
            self.rollback_state(commited_state)
            if self.multipush(tmp_solution, agent_1, agent_2, v):
                if self.clear(tmp_solution, agent_1, agent_2, v):
                    solution += tmp_solution
                    self.exchange(solution, agent_1, agent_2, v)
                    self.reverse(solution, tmp_solution, agent_1, agent_2)
                    print("(swap) End")
                    return True

        return False

    def multipush(self, solution, agent_1, agent_2, v):
        print("(multipush) Start")
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
            
            self.move_agent(solution, r, v_r, waypoint)
            self.move_agent(solution, s, v_s, v_r)
        
        return True

    def clear(self, solution, agent_1, agent_2, v):
        print("(clear) Start")
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
            self.move_agent(tmp_solution, r, self.agents_positions[r], eps)
            self.move_agent(tmp_solution, s, self.agents_positions[s], v)
            
            if self.clear_vertex(tmp_solution, n, {v, eps}):
                if self.clear_vertex(tmp_solution, v1, {v, eps, n}):
                    solution += tmp_solution
                    return True
                break
        
        if not self.clear_vertex(solution, v1, {v}):
            return False
        self.move_agent(solution, r, self.agents_positions[r], v1)

        if not self.clear_vertex(solution, eps, {v, v1, self.agents_positions[s]}):
            return False

        n = neighbours.pop()
        while True:
            if (n != v1) and (n != eps):
                break
            n = neighbours.pop()

        t = self.occupied_vertices[n]

        self.move_agent(solution, t, n, v)
        self.move_agent(solution, t, v, eps)
        self.move_agent(solution, r, self.agents_positions[r], v)
        self.move_agent(solution, s, self.agents_positions[s], v1)

        return self.clear_vertex(solution, eps, {v, v1, n})

    def exchange(self, solution, agent_1, agent_2, v): 
        print("(exchange) Start")
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

        v1 = empty_neighbours.pop()
        v2 = empty_neighbours.pop()
        v_s = self.agents_positions[s]
        self.move_agent(solution, r, v, v1)
        self.move_agent(solution, s, v_s, v)
        self.move_agent(solution, s, v, v2)
        self.move_agent(solution, r, v1, v)
        self.move_agent(solution, r, v, v_s)
        self.move_agent(solution, s, v2, v)

    def circular_buffer_index(self, ind, buff_len):
        if ind < 0:
            return -(abs(ind) % buff_len)
        else:
            return abs(ind) % buff_len

    def rotate(self, solution, queue, v):
        print("(rotate) Start")
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
                        self.move_agent(solution, self.occupied_vertices[move_from], move_from, move_to)
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
                print(c)
                solution += tmp_solution
                v2 = c[ind-1]
                r2 = self.occupied_vertices[v2]
                self.move_agent(solution, r2, v2, v1)
                if not self.swap(solution, r, r2):
                    return False, None
                               
                i_move_from = self.circular_buffer_index(ind - 2, len(c))
                i_move_to = self.circular_buffer_index(ind - 1, len(c))

                while True:
                    move_from = c[i_move_from]
                    move_to = c[i_move_to]
                    self.move_agent(solution, self.occupied_vertices[move_from], move_from, move_to)
                    i_move_to = self.circular_buffer_index(i_move_from, len(c))
                    i_move_from = self.circular_buffer_index(i_move_from - 1, len(c))

                    if c[i_move_from] == v2:
                        break

                self.reverse(solution, tmp_solution, r, r2)
                return True, queue
        return False, None

    def resolve(self, solution, queue):
        print("(resolve) Start")
        
        while len(queue) > 0:
            v = queue[-1]
            print(v)
            if v in self.occupied_vertices:
                r = self.occupied_vertices[v]
                if r in self.successful_agents and self.agents_positions[r] != self.goals[r]:
                    if not self.push(solution, r, self.goals[r], self.successful_agents_positions()):
                        s = self.occupied_vertices[self.goals[r]]
                        print("(resolve) Rec")
                        return self.plan(solution, s, queue)
            queue.pop()
        print("(resolve) End")
        return True

    def reverse(self, solution, tail, agent_1, agent_2):
        print("(reverse) Start")
        for move in reversed(tail):
            if move[0] == agent_1:
                self.move_agent(solution, agent_2, move[2], move[1])
            elif move[0] == agent_2:
                self.move_agent(solution, agent_1, move[2], move[1])
            else:
                self.move_agent(solution, move[0], move[2], move[1])

    def move_agent(self, solution, agent, v_from, v_to):
        # print("\t(move) Agent:", agent, "from", v_from, "to", v_to)
       
        if self.agents_positions[agent] != v_from:
            print(self.debug_prefix,  "Error: move from incorrect position!", agent, v_from, v_to)
            exit()
        if v_to in self.occupied_vertices:
            print(self.debug_prefix,  "Error: move to occupied position!", agent, v_from, v_to)
            exit()
        if v_to not in self.graph.get_neighbours(v_from):
            print(self.debug_prefix,  "Error: move to vertex withou edge!", agent, v_from, v_to)
            exit()

        interfere_v = self.get_interfere_vertices(v_from, v_to)
        if len(interfere_v) != 0:
            print(self.debug_prefix,  "Error: collision", v_from, v_to)
            exit(-10)
        
        # if self.goals[agent] == v_from and v_from in self.reached_goals:
        #     print(self.debug_prefix,  "Alert! Agent ", agent, "moved from goal!")
        # if self.goals[agent] == v_to and v_to in self.reached_goals:
        #     print(self.debug_prefix,  "Alert! Agent ", agent, "moved back to goal!")

        self.empty_vertices.add(v_from)
        self.empty_vertices.remove(v_to)
        self.occupied_vertices.update({v_to : agent})
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

    def get_interfere_vertices(self, v_from, v_to):
        result = set()
        edge_len = self.graph.get_euclidian_distance(v_from, v_to)
        p_from = self.graph.get_vertex_position(v_from)
        p_to = self.graph.get_vertex_position(v_to)
        suspect_zone_size = edge_len + 2 * self._size
        suspect_vert = self.graph.get_vertices_in_zone(self.graph.get_vertex_position(v_from), suspect_zone_size)

        for v in suspect_vert:
            if v == v_from or v == v_to:
                continue
            if self.check_suspect_vertex(p_from, p_to, v):
                result.add(v)
        return result

    def check_suspect_vertex(self, edge_p1, edge_p2, suspect_v) -> bool:
        suspect_p = self.graph.get_vertex_position(suspect_v)

        if dist_point_line_segment(edge_p1, edge_p2, suspect_p) < 2 * self._size:
            return True
        return False
    # def check_reached_goals(self):
    # for goal in self.reached_goals:
    #     print(self.occupied_vertices[goal] ,goal)
    #     if goal not in self.occupied_vertices:
    #         print("reached_goals is not correct")
            

    #     if self.agents_positions[self.occupied_vertices[goal]] != goal:
    #         print("reached_goals is not correct")

        
            