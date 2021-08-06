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
        return True, self.solution

    
    def push(self, agent, target):
        p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[agent], target, {})
        if not p_star_exists:
            print("(push) Path to target vertex not found")
            return False
        
        p_star.pop()
        v_id = p_star.pop()
        while self.agents_positions[agent] != target:
            while v_id in self.empty_vertices:
     
                self.solution.append((agent, self.agents_positions[agent], v_id))
                self.move_agent(agent, self.agents_positions[agent], v_id)                

                if self.agents_positions[agent] == target:
                    return True    
                v_id = p_star.pop()
            
            if self.agents_positions[agent] != target:
                blocked = set()
                blocked.add(self.agents_positions[agent])
                blocked.update(self.reached_goals)

                p_exists, p = path_to_closest_empty_vertex(self.graph, v_id, self.empty_vertices, blocked)
                
                if not p_exists:
                    print("(push) Path to empty vertex not found")
                    return False
                
                blocked.clear()
                v2_id = p.pop(0)
                

                while v_id != v2_id:
                    v1_id = p.pop(0)
                    r1 = self.occupied_vertices[v1_id]
                    
                    self.solution.append((r1, v1_id, v2_id))
                    self.move_agent(r1, v1_id, v2_id)
                    v2_id = v1_id
        return True

    def swap(self, agent):
        p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[agent], self.goals[agent], {}) # TODO save path from push
        if not p_star_exists:
            print("(swap) Path to goal vertex not found")
            return False, None

        second_agent = self.occupied_vertices[p_star[-2]]
        success = False,

        for v in self.graph.get_vertices_degree_geq_3():
            p_exists, p = shortest_path(self.graph, self.agents_positions[agent], v, {})
            if not p_exists:
                continue
            if self.multipush(agent, second_agent, p):
                if self.clear(v, agent, second_agent):
                    success = True
                    break

        if not success:
            print("(swap) Opeartion failed")
            return False, None

        self.execute_swap(agent, second_agent)
        self.reverse()
        if self.goals[second_agent] in self.reached_goals:
            return self.resolve(agent, second_agent, p_star)
        return True, second_agent
        
    def multipush(self, agent_1, agent_2, path):
        local_goal = path[0]
        
        if len(path) < 2:
            return True

        # second agent on the path, need to push second agent before first
        if path[-2] == self.agents_positions[agent_2]: 
            # TODO make it, using only one case (swap variables of agents)
            path.pop()
            v_id = path.pop()
            while self.agents_positions[agent_2] != local_goal:
                while v_id in self.empty_vertices:
                    #TODO save actions to tmp solution
                    self.empty_vertices.add(self.agents_positions[agent_1])
                    self.empty_vertices.remove(v_id)
                    self.occupied_vertices[v_id] = agent_2
                    self.occupied_vertices[self.agents_positions[agent_1]] = agent_1
                    self.occupied_vertices.pop(self.agents_positions[agent_1])
                    self.agents_positions[agent_2] = v_id
                    self.agents_positions[agent_1] = self.agents_positions[agent_2]

                    if self.agents_positions[agent_2] == local_goal:
                        break   
                    v_id = path.pop()
            
                if self.agents_positions[agent_2] != local_goal:
                    blocked = {self.agents_positions[agent_1], self.agents_positions[agent_2]}
                    if not self.push_toward_empty_vertex(self.occupied_vertices[v_id], blocked):
                        blocked.clear()
                        print("(multipush) Push operation of second agent failed")
                        return False
                    blocked.clear()
            blocked = {self.agents_positions[agent_1], self.agents_positions[agent_2]}
            if not self.push_toward_empty_vertex(agent_2, blocked):
                blocked.clear()
                print("(multipush) Last push operation of second agent failed")
                return False
            blocked.clear()
            # Move first agent to empty vertex of degree 3
            self.empty_vertices.add(self.agents_positions[agent_1])
            self.empty_vertices.remove(local_goal)
            self.occupied_vertices.update({local_goal : agent_1})
            self.occupied_vertices.pop(self.agents_positions[agent_1])
            self.agents_positions[agent_1] = local_goal
            return True
        # second agent moves after first
        else:
            path.pop()
            v_id = path.pop()
            while self.agents_positions[agent_1] != local_goal:
                while v_id in self.empty_vertices:
                    #TODO save actions to solution

                    self.empty_vertices.add(self.agents_positions[agent_2])
                    self.empty_vertices.remove(v_id)
                    self.occupied_vertices[v_id] = agent_1
                    self.occupied_vertices[self.agents_positions[agent_1]] = agent_2
                    self.occupied_vertices.pop(self.agents_positions[agent_2])
                    self.agents_positions[agent_1] = v_id
                    self.agents_positions[agent_2] = self.agents_positions[agent_1]

                    if self.agents_positions[agent_1] == local_goal:
                        return True    
                    v_id = path.pop()
            
                if self.agents_positions[agent_1] != local_goal:
                    blocked = {self.agents_positions[agent_1], self.agents_positions[agent_2]}
                    if not self.push_toward_empty_vertex(self.occupied_vertices[v_id], blocked):
                        print("(multipush) Push operation of first agent failed")
                        return False
                    blocked.clear()

            return True

    def clear(self, v, agent_1, agent_2): # TODO reimplement using pseudocode from IROS "Efficient and Complete Centralized Multi-Robot Path Planning"
        # TODO save actions to tmp solution
        neighbours = self.graph.get_neighbours(v)
        empty_neighbours = neighbours & self.empty_vertices
        
        # Two empty neighbour vertices
        if len(empty_neighbours) >= 2:
            return True

        # Try to push neighbour vertices 
        for n_id in neighbours:
            if n_id in empty_neighbours:
                continue
            blocked = empty_neighbours | {self.agents_positions[agent_1], self.agents_positions[agent_2]}
            if self.push_toward_empty_vertex(self.occupied_vertices[n_id], blocked):
                blocked.clear()
                if len(neighbours & self.empty_vertices) >= 2:
                    return True
            blocked.clear()
            
        # Try to move one of neighbouring agent to other position, where it can be pushed out
        v_2 = self.agents_positions[agent_2]
        empty_neighbours = neighbours & self.empty_vertices
        blocked = empty_neighbours | {v}
        if not self.push_toward_empty_vertex(agent_2, blocked):
            blocked.clear()
            print("(clear) Path to empty vertex not found")
            return False
        blocked.clear()

        # move first agent to position of second
        self.empty_vertices.add(v)
        self.empty_vertices.remove(v_2)
        self.occupied_vertices.update({v_2 : agent_1})
        self.occupied_vertices.pop(v)
        self.agents_positions[agent_1] = v_2
        # n_id = (self.graph.get_neighbours(v) - empty_neighbours).pop()
        for n_id in neighbours: 
            if n_id in empty_neighbours:
                continue
            n_agent = self.occupied_vertices[n_id]

            for e_id in empty_neighbours:
                # move one of the neighbouring agent to old position of first
                self.empty_vertices.add(self.agents_positions[n_agent])
                self.empty_vertices.remove(v)
                self.occupied_vertices.update({v : n_agent})
                self.occupied_vertices.pop(self.agents_positions[n_agent])
                self.agents_positions[n_agent] = v

                # move one of the neighbouring agent to one of empty neighboring vertex
                self.empty_vertices.add(self.agents_positions[n_agent])
                self.empty_vertices.remove(e_id)
                self.occupied_vertices.update({e_id : n_agent})
                self.occupied_vertices.pop(self.agents_positions[n_agent])
                self.agents_positions[n_agent] = e_id


                # move first agent to v
                self.empty_vertices.add(v_2)
                self.empty_vertices.remove(v)
                self.occupied_vertices.update({v : agent_1})
                self.occupied_vertices.pop(v_2)
                self.agents_positions[agent_1] = v

                # move second agent to its old position
                self.empty_vertices.add(self.agents_positions[agent_2])
                self.empty_vertices.remove(v_2)
                self.occupied_vertices.update({v_2 : agent_2})
                self.occupied_vertices.pop(self.agents_positions[agent_2])
                self.agents_positions[agent_2] = v_2

                blocked = (neighbours & self.empty_vertices) | {v, v_2}
                if self.push_toward_empty_vertex(n_agent, blocked):
                    blocked.clear()
                    if len(neighbours & self.empty_vertices) > 2"
                        return True
                    break     
        return False

    def push_toward_empty_vertex(self, agent, blocked):
        v_id = self.agents_positions[agent]
        p_exists, p = path_to_closest_empty_vertex(self.graph, v_id, self.empty_vertices, blocked)
                
        if not p_exists:
            print("(push_toward_empty_vertex) Path to empty vertex not found")
            return False
                
        v2_id = p.pop(0)
                
        while v_id != v2_id:
            v1_id = p.pop(0)
            r1 = self.occupied_vertices[v1_id]
            
            # self.solution.append((r1, v1_id, v2_id))
            self.move_agent(r1, v1_id, v2_id)
            v2_id = v1_id
        
        return True
            
    def execute_swap(self, agent_1, agent_2):
        v = self.agents_positions[agent_1]
        v2 = self.agents_positions[agent_2]
        neighbours = self.graph.get_neighbours(v)
        empty_neighbours = neighbours & self.empty_vertices

        if len(empty_neighbours) < 2:
            print("Clean operation failed")
            exit()
        
        n1 = empty_neighbours[0]
        n2 = empty_neighbours[1]

        self.move_agent(agent_1, v, n1)
        self.move_agent(agent_2, v2, v)
        self.move_agent(agent_2, v, n2)
        self.move_agent(agent_1, n1, v)
        self.move_agent(agent_1, v, v2)
        self.move_agent(agent_2, n2, v)

    def reverse(self):
        raise NotImplementedError

    def resolve(self, agent_1, agent_2, path):
        reached_goals = copy.deepcopy(self.reached_goals)
        t = path[-3]
        s_pos = self.agents_positions[agent_2]
        s_goal = self.goals[agent_2]
        self.reached_goals.add(s_pos)
        self.reached_goals.remove(s_goal)

        if self.push(agent_1, t):
            self.reached_goals = reached_goals
            self.move_agent(agent_2, s_pos, s_goal)
            return True
        else:
            r2 = r
            swap_res, swap_agent = self.swap(r2)
            while swap_res:
                if self.agents_positions[agent_2] == s_goal or self.push(agent_2, s_goal):
                    self.reached_goals = reached_goals
                    return True
                elif self.agents_positions[r2] == self.goals[r2]:
                    self.reached_goals.add(self.goals[r2])
                    r2 = swap_agent
                    p_star = shortest_path(self.graph, self.agents_positions[r2], self.goals[r2], {})
                    resolve_res = self.resolve(r2, agent_2, p_star)
                    self.reached_goals = reached_goals
                    return resolve_res

                swap_res, swap_agent = self.swap(r2)

        self.reached_goals = reached_goals
        return False

    def move_agent(self, agent, v_from, v_to):
        # TODO debug check for agent position and target
        self.empty_vertices.add(v_from)
        self.empty_vertices.remove(v_to)
        self.occupied_vertices.update({v_to : agent})
        self.occupied_vertices.pop(v_from)
        self.agents_positions[agent] = v_to