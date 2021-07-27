class PushAndSwap:
    
    def __init__(self, graph, agents):
        self.graph = graph
        self.agents = agents
        self.reached_goals = {}


    def solve(self):
        for agent in self.agents:
            while not agent.finished():
                if not push():
                    if not swap():
                        return False
            self.reached_goals.add(agent.goal())
        return True

    
    def push():
        pass

    def swap():
        pass