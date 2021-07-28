from pathplanner import shortest_path

class PushAndSwap:
    
    def __init__(self, graph, agents):
        self.graph = graph
        self.agents = agents

        raise NotImplementedError
        self.agents_positions = {} # TODO
        self.reached_goals = {} # TODO
        self.empty_verticies = {} # TODO
        self.occupied_verticies = {} # TODO


    def solve(self):
        for agent in self.agents:
            while not agent.finished():
                if not push():
                    if not swap():
                        return False
            self.reached_goals.add(agent.goal())
        return True

    
    def push(agent):
        p_exists, p_star = shortest_path(self.graph, self.agents_positions[agent.a_id], agent.goal_id, {})
        if not p_exists:
            return False
        
        p_star.pop()
        v_id = p_star.pop()
        while self.agents_positions[agent.a_id] != agent.goal_id:
            while v_id in self.empty_verticies:
                # TODO Save states

                self.empty_verticies.add(self.agents_positions[agent.a_id])
                self.empty_verticies.remove(v_id)
                self.occupied_verticies.add(v_id)
                self.occupied_verticies.remove(self.agents_positions[agent.a_id])

                self.agents_positions[agent.a_id] = v_id
                
                if self.agents_positions[agent.a_id] == agent.goal_id:
                    return True    
                v_id = p_star.pop()
            
            if self.agents_positions[agent.a_id] != agent.goal_id:
                self.occupied_verticies.add(self.agents_positions[agent.a_id])
                self.occupied_verticies.update(self.occupied_verticies)


    def swap():
        pass