from heapq import heappop, heappush
from graph import Graph, Node

class Open:
    def __init__(self):
        self.prioritized_queue = []    
        self.nodes = {}  
    

    def __iter__(self):
        raise NotImplementedError
        # return iter(self.nodes.values())
    

    def __len__(self):
        return len(self.nodes)


    def is_empty(self):
        return len(self.nodes) == 0


    def add_node(self, item):
        raise NotImplementedError
        # ij = item.i, item.j, item.speed, item.orientation
        # oldNode = self.ij_to_node.get(ij)
        # if oldNode is None or item.g < oldNode.g:
        #     self.ij_to_node[ij] = item              
        #     heappush(self.prioritizedQueue, item)


    def get_best_node(self):
        raise NotImplementedError
        # bestNode = heappop(self.prioritizedQueue)
        # ij = bestNode.i, bestNode.j, bestNode.speed, bestNode.orientation
        # while self.ij_to_node.pop(ij, None) is None:
        #     bestNode = heappop(self.prioritizedQueue)
        #     ij = bestNode.i, bestNode.j, bestNode.speed, bestNode.orientation
        # return bestNode


class Closed:
    def __init__(self):
        self.elements = {}


    def __iter__(self):
        return iter(self.elements.values())
    

    def __len__(self):
        return len(self.elements)


    def add_node(self, item):
        raise NotImplementedError
        # self.elements[(item.i, item.j, item.speed, item.orientation)]=item


    def was_expanded(self, item):
        raise NotImplementedError
        # return (item.i, item.j, item.speed, item.orientation) in self.elements.keys()


def astar(graph, start_id, goal_id, occupied):
    OPEN = Open()
    CLOSED = Closed()
    start_node = Node(start_id, 0, graph.get_euclidian_distance(start_id, goal_id))
    OPEN.add_node(startNode)

    while not OPEN.is_empty():
        current_node = OPEN.get_best_node()
        CLOSED.add_node(current_node)
        
        if current_node.v_id == goal_id:
            return True, current_node
        
        for neighbour_id in graph.get_neighbours(current_node.v_id):
            new_node = Node(neighbour_id)
            if not CLOSED.was_expanded(new_node) and neighbour_id not in occupied:
                new_node.g = current_node.g + graph.get_euclidian_distance(current_node.v_id, neighbour_id)
                new_node.h = graph.get_euclidian_distance(neighbour_id, goal_id)
                new_node.F = new_node.g + new_node.h
                new_node.parent = current_node
                OPEN.add_node(new_node)

    return False, None


def shortest_path(graph, start_id, goal_id, occupied):
    raise NotImplementedError