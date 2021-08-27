from pathplanner import shortest_path, path_to_closest_empty_vertex
import copy

class PushAndSwap:
    
    def __init__(self, graph, agents, starts, goals):
        self.graph = graph
        self.agents = agents
        self.starts = starts
        self.goals = goals

        self.agents_positions = copy.deepcopy(starts)
        self.reached_goals = set() 
        self.empty_vertices = copy.deepcopy(graph.vertices)
        self.occupied_vertices = dict()
        self.solution = []
        self.reversed_plan = []

        self.debug_prefix = ""

        for agent, vert in starts.items():
            self.occupied_vertices.update({vert : agent})
            self.empty_vertices.remove(vert)

    def solve(self):
        for agent in self.agents:
            while self.agents_positions[agent] != self.goals[agent]:
                if not self.push(agent, self.goals[agent]):
                    swap_res, _ = self.swap(agent)
                    if not swap_res:
                        return False, None
            self.reached_goals.add(self.goals[agent])
            self.check_reached_goals()
        return True, self.solution

    def push(self, agent, target):
        print(self.debug_prefix,  "(push) Start. Agent: ", agent, target)
        p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[agent], target, {})

        if not p_star_exists:
            print(self.debug_prefix,  "(push) Path to target vertex not found")
            return False

        p_star.pop()
        v_id = p_star.pop()

        while self.agents_positions[agent] != target:
            while v_id in self.empty_vertices:
                self.move_agent(agent, self.agents_positions[agent], v_id)                

                if self.agents_positions[agent] == target:
                    print(self.debug_prefix,  "(push) End")
                    return True    
                v_id = p_star.pop()
            
            if self.agents_positions[agent] != target:
                blocked = set()
                blocked.add(self.agents_positions[agent])
                blocked.update(self.reached_goals)

                if v_id in blocked:
                    print(self.debug_prefix,  "(push) Path to empty vertex not found. Agent: ", agent)
                    return False

                p_exists, p = path_to_closest_empty_vertex(self.graph, v_id, self.empty_vertices, blocked)

                if not p_exists:
                    print(self.debug_prefix,  "(push) Path to empty vertex not found. Agent: ", agent)
                    return False
                
                blocked.clear()
                v2_id = p.pop(0)
                
                while v_id != v2_id:
                    v1_id = p.pop(0)
                    r1 = self.occupied_vertices[v1_id]
                    self.move_agent(r1, v1_id, v2_id)
                    v2_id = v1_id

        print(self.debug_prefix,  "(push) End")
        return True

    def swap(self, agent):
        print(self.debug_prefix,  "(swap) Start. Agent: ", agent)
        p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[agent], self.goals[agent], {}) # TODO save path from push
        
        if not p_star_exists:
            print(self.debug_prefix,  "(swap) Path to goal vertex not found")
            return False, None

        second_agent = self.occupied_vertices[p_star[-2]]       
        pos_1 = self.agents_positions[agent]
        pos_2 = self.agents_positions[second_agent]
        
        print(self.debug_prefix, "(swap) Agent 2: ", second_agent)
        print(self.debug_prefix, "(swap) pos 1", pos_1, "goal 1", self.goals[agent] )
        print(self.debug_prefix, "(swap) pos 2", pos_2, "goal 2", self.goals[second_agent] )

        success = False

        tmp_plan = copy.deepcopy(self.solution)
        tmp_empty = copy.deepcopy(self.empty_vertices)
        tmp_occup = copy.deepcopy(self.occupied_vertices)
        tmp_pos = copy.deepcopy(self.agents_positions)

        
        for v in self.graph.get_vertices_degree_geq_3():
            self.reversed_plan = []
            p_exists, p = shortest_path(self.graph, self.agents_positions[agent], v, {})

            if not p_exists:
                continue
            if self.multipush(agent, second_agent, p):
                if self.clear(v, agent, second_agent):
                    success = True
                    break

            self.solution = copy.deepcopy(tmp_plan)
            self.empty_vertices = copy.deepcopy(tmp_empty)
            self.occupied_vertices = copy.deepcopy(tmp_occup)
            self.agents_positions = copy.deepcopy(tmp_pos)

        if not success:
            print(self.debug_prefix, "(swap) Opeartion failed")
            return False, None
        self.execute_swap(agent, second_agent)

        self.reverse()
        self.reversed_plan = []

        print(self.debug_prefix, self.agents_positions[agent], self.agents_positions[second_agent])
        if self.agents_positions[agent] != pos_2 or self.agents_positions[second_agent] != pos_1:
            print(self.debug_prefix, "(swap) Error!")
            exit()

        if self.goals[second_agent] in self.reached_goals and pos_2 == self.goals[second_agent]:
            print(self.debug_prefix, "(swap) Resolve is needed!")
            print(self.debug_prefix, second_agent, self.goals[second_agent], self.reached_goals)

            resolve_result = self.resolve(agent, second_agent, p_star), second_agent

            print(self.debug_prefix, "(swap) End with resolve result:", resolve_result)
            return resolve_result
        
        print(self.debug_prefix, "(swap) End")
        return True, second_agent
        
    def multipush(self, agent_1, agent_2, path):
        print(self.debug_prefix, "(multipush) Start. Agents:", agent_1, agent_2)

        if len(path) < 2:
            return True

        local_goal = path[0]
        # Second agent on the path, need to push second agent before first
        if path[-2] == self.agents_positions[agent_2]: 
            # TODO make it, using only one case (swap variables of agents)
            print(self.debug_prefix, "(multipush) Case 1")
            path.pop()
            path.pop()

            if len(path) > 0:
                v_id = path.pop()

                while self.agents_positions[agent_2] != local_goal:
                    while v_id in self.empty_vertices:
                        v2_id = self.agents_positions[agent_2]

                        self.move_agent(agent_2, self.agents_positions[agent_2], v_id, True, agent_1)
                        self.move_agent(agent_1, self.agents_positions[agent_1], v2_id, True, agent_2)

                        if self.agents_positions[agent_2] == local_goal:
                            break   

                        v_id = path.pop()
                
                    if self.agents_positions[agent_2] != local_goal:
                        blocked = {self.agents_positions[agent_1], self.agents_positions[agent_2]}

                        if not self.push_toward_empty_vertex(self.occupied_vertices[v_id], blocked, True):
                            blocked.clear()
                            print(self.debug_prefix, "(multipush) Push operation of second agent failed")
                            return False

                        blocked.clear()

            blocked = {self.agents_positions[agent_1], self.agents_positions[agent_2]}

            if not self.push_toward_empty_vertex(agent_2, blocked, True):
                blocked.clear()
                print(self.debug_prefix, "(multipush) Last push operation of second agent failed")
                return False
            self.reversed_plan[0] = (agent_1, self.reversed_plan[0][1], self.reversed_plan[0][2])
            blocked.clear()
            print(self.debug_prefix, "(multipush) Last move")
            self.move_agent(agent_1, self.agents_positions[agent_1], local_goal, True, agent_2) # Move first agent to empty vertex of degree 3
            print(self.debug_prefix, "(multipush) End.")
            return True
        else:  
            # Second agent moves after first
            print(self.debug_prefix, "(multipush) Case 2")
            path.pop()
            v_id = path.pop()

            while self.agents_positions[agent_1] != local_goal:
                while v_id in self.empty_vertices:
                    v2_id = self.agents_positions[agent_1]
                    self.move_agent(agent_1, self.agents_positions[agent_1], v_id, True, agent_2)
                    self.move_agent(agent_2, self.agents_positions[agent_2], v2_id, True, agent_1)

                    if self.agents_positions[agent_1] == local_goal:
                        return True    
                    v_id = path.pop()
            
                if self.agents_positions[agent_1] != local_goal:
                    blocked = {self.agents_positions[agent_1], self.agents_positions[agent_2]}

                    if not self.push_toward_empty_vertex(self.occupied_vertices[v_id], blocked, True):
                        print(self.debug_prefix, "(multipush) Push operation of first agent failed")
                        return False

                    blocked.clear()
            print(self.debug_prefix, "(multipush) End.")
            return True

    def clear(self, v, agent_1, agent_2): 
        print(self.debug_prefix, "(clear) Start. Agents:", agent_1, agent_2)
        # TODO reimplement using pseudocode from IROS "Efficient and Complete Centralized Multi-Robot Path Planning"
        # TODO save actions to tmp solution
        neighbours = self.graph.get_neighbours(v)
        empty_neighbours = neighbours & self.empty_vertices
        
        # Two empty neighbour vertices
        if len(empty_neighbours) >= 2:
            print(self.debug_prefix, "(clear) End.")
            return True

        # Try to push neighbour vertices 
        print(self.debug_prefix, "(clear) Case 1 ")
        for n_id in neighbours:
            if n_id in empty_neighbours or n_id == self.agents_positions[agent_1] or n_id == self.agents_positions[agent_2]:
                continue
            blocked = empty_neighbours | {self.agents_positions[agent_1], self.agents_positions[agent_2]}
            if self.push_toward_empty_vertex(self.occupied_vertices[n_id], blocked, True):
                blocked.clear()
                if len(neighbours & self.empty_vertices) >= 2:
                    print(self.debug_prefix, "(clear) End.")
                    return True
            blocked.clear()
            
        # Try to move one of neighbouring agent to other position, where it can be pushed out
        print(self.debug_prefix, "(clear) Case 2")

        v_2 = self.agents_positions[agent_2]
        empty_neighbours = neighbours & self.empty_vertices
        blocked = empty_neighbours | {v}
        if not self.push_toward_empty_vertex(agent_2, blocked, True):
            blocked.clear()
            print(self.debug_prefix, "(clear) Path to empty vertex not found")
            return False
        self.reversed_plan[0] = (agent_1, self.reversed_plan[0][1], self.reversed_plan[0][2])
        blocked.clear()
        
        self.move_agent(agent_1, v, v_2, True, agent_2) # move first agent to position of second
        v_3 = self.agents_positions[agent_2]
        print(self.debug_prefix, v, v_2, v_3)

        for n_id in neighbours: 
            empty_neighbours = neighbours & self.empty_vertices
            
            if n_id in empty_neighbours or n_id == v_2:
                continue
            
            n_agent = self.occupied_vertices[n_id]
            for e_id in empty_neighbours:
               
                self.move_agent(n_agent, self.agents_positions[n_agent], v, True)     # move one of the neighbouring agent to old position of first      
                self.move_agent(n_agent, self.agents_positions[n_agent], e_id, True)  # move one of the neighbouring agent to one of empty neighboring vertex

                blocked = (neighbours & self.empty_vertices) | {v, v_2, v_3}
                if self.push_toward_empty_vertex(n_agent, blocked, True):
                    blocked.clear()
                    self.move_agent(agent_1, v_2, v, True, agent_2)                                # move first agent to v
                    self.move_agent(agent_2, self.agents_positions[agent_2], v_2, True, agent_1)   # move second agent to its old position
                    if len(neighbours & self.empty_vertices) >= 2:
                        print(self.debug_prefix, "(clear) End.")
                        return True
                    break 
        print(self.debug_prefix, "(clear) Operation failed")    
        return False

    def push_toward_empty_vertex(self, agent, blocked, need_to_reverce = False):
        print(self.debug_prefix, "(push toward empty vertex) Start. Agent:", agent)
        v_id = self.agents_positions[agent]
        p_exists, p = path_to_closest_empty_vertex(self.graph, v_id, self.empty_vertices, blocked)
                
        if not p_exists:
            print(self.debug_prefix, "(push_toward_empty_vertex) Path to empty vertex not found")
            return False
                
        v2_id = p.pop(0)
                
        while v_id != v2_id:
            v1_id = p.pop(0)
            r1 = self.occupied_vertices[v1_id]
            self.move_agent(r1, v1_id, v2_id, need_to_reverce)
            v2_id = v1_id
        print(self.debug_prefix, "(push toward empty vertex) End")
        return True
            
    def execute_swap(self, agent_1, agent_2):  
        print(self.debug_prefix, "(execute swap) Start. Agents:", agent_1, agent_2)
        v = self.agents_positions[agent_1]
        v2 = self.agents_positions[agent_2]
        neighbours = self.graph.get_neighbours(v)
        empty_neighbours = neighbours & self.empty_vertices

        if len(empty_neighbours) < 2:
            print(self.debug_prefix, "Error: clean operation failed")
            exit()
        
        n1 = empty_neighbours.pop()
        n2 = empty_neighbours.pop()
        self.move_agent(agent_1, v, n1)
        self.move_agent(agent_2, v2, v)
        self.move_agent(agent_2, v, n2)
        self.move_agent(agent_1, n1, v)
        self.move_agent(agent_1, v, v2)
        self.move_agent(agent_2, n2, v)
        print(self.debug_prefix, "(execute swap) End")

    def resolve(self, agent_1, agent_2, path):
        print(self.debug_prefix, "(resolve) Start. Agents:", agent_1, agent_2)

        if(self.agents_positions[agent_1] != self.goals[agent_2]):
            print(self.debug_prefix, "(resolve) Error", self.agents_positions[agent_1], self.agents_positions[agent_2])
            print(self.debug_prefix, "(resolve) Error", self.goals[agent_1], self.goals[agent_2])
            exit()

        print(self.debug_prefix, path)

        r = agent_1
        reached_goals = copy.deepcopy(self.reached_goals)

        print(self.debug_prefix, self.agents_positions[agent_1], self.agents_positions[agent_2])
        print(self.debug_prefix, self.goals[agent_1], self.goals[agent_2])
        
        if self.goals[agent_1] == self.agents_positions[agent_2]:
            t = self.goals[agent_1]
        else:
            t = path[-3]

        s_pos = self.agents_positions[agent_2]
        s_goal = self.goals[agent_2]
        self.reached_goals.add(s_pos)
        self.reached_goals.discard(s_goal)

        if (self.agents_positions[agent_2] != s_goal) and (s_goal not in self.graph.get_neighbours(self.agents_positions[agent_2])):
            print(self.debug_prefix, "PnS Error!")
            exit()

        if self.push(agent_1, t):
            print(self.debug_prefix, "(resolve) push completed")
            self.reached_goals = copy.deepcopy(reached_goals)
            if self.agents_positions[agent_2] != self.goals[agent_2]:
                self.move_agent(agent_2, s_pos, s_goal)
            print(self.debug_prefix, "(resolve) End")
            return True
        else:
            r2 = r

            tmp_prefix = self.debug_prefix
            self.debug_prefix += '\t'
            print(self.reached_goals)
            swap_res, swap_agent = self.swap(r2)
            self.debug_prefix = tmp_prefix

            while swap_res:
                print(self.debug_prefix, "(resolve) swap while")
                if (self.agents_positions[agent_2] != s_goal) and (s_goal not in self.graph.get_neighbours(self.agents_positions[agent_2])):
                    print(self.debug_prefix, "PnS Error!")
                    exit()

                if self.agents_positions[agent_2] == s_goal or self.push(agent_2, s_goal):
                    self.reached_goals = copy.deepcopy(reached_goals)
                    return True
                elif self.agents_positions[r2] == self.goals[r2]:
                    self.reached_goals.add(self.goals[r2])
                    r2 = swap_agent
                    p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[r2], self.goals[r2], {})
                    
                    if not p_star_exists:
                        self.reached_goals = copy.deepcopy(reached_goals)
                        return False
                    
                    tmp_prefix = self.debug_prefix
                    self.debug_prefix += '\t'
                    resolve_res = self.resolve(r2, agent_2, p_star)
                    self.debug_prefix = tmp_prefix
                    self.reached_goals = copy.deepcopy(reached_goals)
                    
                    return resolve_res
                
                tmp_prefix = self.debug_prefix
                self.debug_prefix += '\t'
                swap_res, swap_agent = self.swap(r2)
                self.debug_prefix = tmp_prefix

        self.reached_goals = copy.deepcopy(reached_goals)
        print(self.debug_prefix,  "(resolve) Operaion failed")
        return False

    def reverse(self):
        print(self.debug_prefix,  "(reverse) Start")
        
        for move in self.reversed_plan:
            self.move_agent(move[0], move[1], move[2])

        print(self.debug_prefix,  "(reverse) End")

    def move_agent(self, agent, v_from, v_to, need_to_reverse = False, other_agent = None):
        # print(self.debug_prefix,  "\t(move) Agent:", agent, "from", v_from, "to", v_to)

        if self.goals[agent] == v_from and v_from in self.reached_goals:
            print(self.debug_prefix,  "Alert! Agent ", agent, "moved from goal!")
        if self.agents_positions[agent] != v_from:
            print(self.debug_prefix,  "Error: move from incorrect position!", agent, v_from, v_to)
            exit()
        if v_to in self.occupied_vertices:
            print(self.debug_prefix,  "Error: move to occupied position!", agent, v_from, v_to)
            exit()
        if v_to not in self.graph.get_neighbours(v_from):
            print(self.debug_prefix,  "Error: move to vertex withou edge!", agent, v_from, v_to)
            exit()

        self.empty_vertices.add(v_from)
        self.empty_vertices.remove(v_to)
        self.occupied_vertices.update({v_to : agent})
        self.occupied_vertices.pop(v_from)
        self.agents_positions[agent] = v_to
        self.solution.append((agent, v_from, v_to))

        if need_to_reverse:
            if other_agent is None:
                self.reversed_plan.insert(0, (agent, v_to, v_from))
            else:
                self.reversed_plan.insert(0, (other_agent, v_to, v_from))

    def check_reached_goals(self):
        for goal in self.reached_goals:
            print(self.occupied_vertices[goal] ,goal)
            if goal not in self.occupied_vertices:
                print("reached_goals is not correct")
                exit()

            if self.agents_positions[self.occupied_vertices[goal]] != goal:
                print("reached_goals is not correct")
                exit()