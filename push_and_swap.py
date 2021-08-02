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
                    if not self.swap():
                        return False, None
            self.reached_goals.add(self.goals[agent])
        return True, self.solution

    
    def push(self, agent):
        p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[agent], self.goals[agent], {})
        if not p_star_exists:
            print(agent, "Path not found 1")
            return False
        
        p_star.pop()
        v_id = p_star.pop()
        while self.agents_positions[agent] != self.goals[agent]:
            print(self.agents_positions[agent], self.goals[agent])
            while v_id in self.empty_verticies:
                # TODO Save states

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

        
                print("empty:", self.empty_verticies)
                print("positions:", self.agents_positions)
                print("reached:", self.reached_goals)
                print("occupied:", self.occupied_verticies)

                p_exists, p = path_to_closest_empty_vertex(self.graph, v_id, self.empty_verticies, blocked)
                
                if not p_exists:
                    print(agent, v_id, "Path not found 2")
                    return False
                
                blocked.clear()
                print("path:", p)


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

    def swap(self):
        return False