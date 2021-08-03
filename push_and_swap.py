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
        self.empty_verticies = copy.deepcopy(graph.verticies)
        self.occupied_verticies = dict()
        self.solution = [] 

        for agent, vert in starts.items():
            self.occupied_verticies.update({vert : agent})
            self.empty_verticies.remove(vert)


    def solve(self):
        for agent in self.agents:
            while self.agents_positions[agent] != self.goals[agent]:
                if not self.push(agent):
                    if not self.swap(agent):
                        return False, None
            self.reached_goals.add(self.goals[agent])
        return True, self.solution

    
    def push(self, agent):
        p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[agent], self.goals[agent], {})
        if not p_star_exists:
            print("(push) Path to goal vertex not found")
            return False
        
        p_star.pop()
        v_id = p_star.pop()
        while self.agents_positions[agent] != self.goals[agent]:
            while v_id in self.empty_verticies:
     
                self.solution.append((agent, self.agents_positions[agent], v_id))
                self.empty_verticies.add(self.agents_positions[agent])
                self.empty_verticies.remove(v_id)
                self.occupied_verticies.update({v_id : agent})
                self.occupied_verticies.pop(self.agents_positions[agent])
                self.agents_positions[agent] = v_id
                

                if self.agents_positions[agent] == self.goals[agent]:
                    return True    
                v_id = p_star.pop()
            
            if self.agents_positions[agent] != self.goals[agent]:
                blocked = set()
                blocked.add(self.agents_positions[agent])
                blocked.update(self.reached_goals)

    

                p_exists, p = path_to_closest_empty_vertex(self.graph, v_id, self.empty_verticies, blocked)
                
                if not p_exists:
                    print("(push) Path to empty vertex not found")
                    return False
                
                blocked.clear()
                v2_id = p.pop(0)
                

                while v_id != v2_id:
                    v1_id = p.pop(0)
                    r1 = self.occupied_verticies[v1_id]
                    
                    self.solution.append((r1, v1_id, v2_id))

                    self.empty_verticies.add(v1_id)
                    self.empty_verticies.remove(v2_id)
                    self.occupied_verticies.update({v2_id : r1})
                    self.occupied_verticies.pop(v1_id)
                    self.agents_positions[r1] = v2_id
                    v2_id = v1_id
        return True

    def swap(self, agent):
        p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[agent], self.goals[agent], {}) # TODO save path from push
        if not p_star_exists:
            print("(swap) Path to goal vertex not found")
            return False

        second_agent = self.occupied_verticies[p_star[-2]]
        success = False

        for v in self.graph.get_verticies_degree_geq_3():
            p_exists, p = shortest_path(self.graph, self.agents_positions[agent], v, {})
            if not p_exists:
                continue
            if self.multipush(agent, second_agent, p):
                if self.clear(v, agent, second_agent):
                    success = True
                    break

        if not success:
            print("(swap) Opeartion failed")
            return False

        self.execute_swap(agent, second_agent)
        self.reverse()
        if self.goals[second_agent] in self.reached_goals:
            return self.resolve(agent, second_agent)
        return True
        

    def multipush(self, agent_1, agent_2, path):
        local_goal = path[0]
        if len(path) < 2:
            return True

        if path[-2] == self.agents_positions[agent_2]: # TODO make it, using only one case (swap variables of agents)
            path.pop()
            v_id = path.pop()
            while self.agents_positions[agent_2] != local_goal:
                while v_id in self.empty_verticies:
                    #TODO save actions to solution

                    # self.solution.append((agent, self.agents_positions[agent], v_id))

                    self.empty_verticies.add(self.agents_positions[agent_1])
                    self.empty_verticies.remove(v_id)

                    self.occupied_verticies[v_id] = agent_2
                    self.occupied_verticies[self.agents_positions[agent_1]] = agent_1
                    self.occupied_verticies.pop(self.agents_positions[agent_1])

                    self.agents_positions[agent_2] = v_id
                    self.agents_positions[agent_1] = self.agents_positions[agent_2]

                    if self.agents_positions[agent_2] == local_goal:
                        break   
                    v_id = path.pop()
            

                if self.agents_positions[agent_2] != local_goal:
                    blocked = set()
                    blocked.add(self.agents_positions[agent_1])
                    blocked.add(self.agents_positions[agent_2])
                    p_exists, p = path_to_closest_empty_vertex(self.graph, v_id, self.empty_verticies, blocked)
                
                    if not p_exists:
                        print("(multipush) Path to empty vertex not found")
                        return False
                
                    blocked.clear()
                    v2_id = p.pop(0)

                    while v_id != v2_id:
                        v1_id = p.pop(0)
                        r1 = self.occupied_verticies[v1_id]
                        
                        # self.solution.append((r1, v1_id, v2_id))

                        self.empty_verticies.add(v1_id)
                        self.empty_verticies.remove(v2_id)
                        self.occupied_verticies.update({v2_id : r1})
                        self.occupied_verticies.pop(v1_id)
                        self.agents_positions[r1] = v2_id
                        v2_id = v1_id

            blocked = set()
            blocked.add(self.agents_positions[agent_1])
            blocked.add(self.agents_positions[agent_2])
            p_exists, p = path_to_closest_empty_vertex(self.graph, local_goal, self.empty_verticies, blocked)

            if not p_exists:
                print("(multipush) Path to empty vertex not found")
                return False

            blocked.clear()
            v2_id = p.pop(0)

            while local_goal != v2_id:
                v1_id = p.pop(0)
                r1 = self.occupied_verticies[v1_id]
                
                # self.solution.append((r1, v1_id, v2_id))

                self.empty_verticies.add(v1_id)
                self.empty_verticies.remove(v2_id)
                self.occupied_verticies.update({v2_id : r1})
                self.occupied_verticies.pop(v1_id)
                self.agents_positions[r1] = v2_id
                v2_id = v1_id


            self.empty_verticies.add(self.agents_positions[agent_1])
            self.empty_verticies.remove(local_goal)
            self.occupied_verticies.update({local_goal : agent_1})
            self.occupied_verticies.pop(self.agents_positions[agent_1])
            self.agents_positions[agent_1] = local_goal

            return True
        else:
            path.pop()
            v_id = path.pop()
            while self.agents_positions[agent_1] != local_goal:
                while v_id in self.empty_verticies:
                    #TODO save actions to solution

                    # self.solution.append((agent, self.agents_positions[agent], v_id))

                    self.empty_verticies.add(self.agents_positions[agent_2])
                    self.empty_verticies.remove(v_id)

                    self.occupied_verticies[v_id] = agent_1
                    self.occupied_verticies[self.agents_positions[agent_1]] = agent_2
                    self.occupied_verticies.pop(self.agents_positions[agent_2])

                    self.agents_positions[agent_1] = v_id
                    self.agents_positions[agent_2] = self.agents_positions[agent_1]

                    if self.agents_positions[agent_1] == local_goal:
                        return True    
                    v_id = path.pop()
            

                if self.agents_positions[agent_1] != local_goal:
                    blocked = set()
                    blocked.add(self.agents_positions[agent_1])
                    blocked.add(self.agents_positions[agent_2])
                    p_exists, p = path_to_closest_empty_vertex(self.graph, v_id, self.empty_verticies, blocked)
                
                    if not p_exists:
                        print("(multipush) Path to empty vertex not found")
                        return False
                
                    blocked.clear()
                    v2_id = p.pop(0)

                    while v_id != v2_id:
                        v1_id = p.pop(0)
                        r1 = self.occupied_verticies[v1_id]
                        
                        # self.solution.append((r1, v1_id, v2_id))

                        self.empty_verticies.add(v1_id)
                        self.empty_verticies.remove(v2_id)
                        self.occupied_verticies.update({v2_id : r1})
                        self.occupied_verticies.pop(v1_id)
                        self.agents_positions[r1] = v2_id
                        v2_id = v1_id
            return True

    def clear(self, v, agent_1, agent_2):
        

    def execute_swap(self, agent_1, agent_2):
        raise NotImplementedError
    
    def reverse(self):
        raise NotImplementedError

    def resolve(self, agent_1, agent_2):
        raise NotImplementedError