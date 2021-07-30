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

        for agent, vert in starts:
            self.occupied_verticies.update({vert : agent})
            self.empty_verticies.remove(vert)


    def solve(self):
        for agent in self.agents:
            while not agent.finished():
                if not self.push(agent):
                    if not self.swap():
                        return False
            self.reached_goals.add(self.goals[agent])
        return True

    
    def push(self, agent):
        p_star_exists, p_star = shortest_path(self.graph, self.agents_positions[agent], self.goals[agent], {})
        if not p_star_exists:
            return False
        
        p_star.pop()
        v_id = p_star.pop()
        while self.agents_positions[agent] != self.goals[agent]:
            while v_id in self.empty_verticies:
                # TODO Save states

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
                blocked.update(self.occupied_verticies.keys())
                p_exists, p = path_to_closest_empty_vertex(self.graph, self.starts[agent], self.empty_verticies, blocked)
                
                if not p_exists:
                    return False
                
                blocked.clear()
                
                v2_id = p.pop(0)
                v1_id = p.pop(0)

                while v1_id != v2_id:
                    r1 = self.occupied_verticies[v1_id]

                    self.empty_verticies.add(v1_id)
                    self.empty_verticies.remove(v2_id)
                    self.occupied_verticies.update({v2_id : r1})
                    self.occupied_verticies.pop(v1_id)
                    self.agents_positions[r1] = v2_id
                    v2_id = v1_id
                    v1_id = p.pop(0)
        return True

    def swap(self):
        return False