from heapq import heappop, heappush
from .graph import Graph, Node


class Open:
    def __init__(self):
        self.prioritized_queue = []    
        self.nodes = {}  
    
    def __iter__(self):
        return iter(self.nodes.values())
    
    def __len__(self):
        return len(self.nodes)

    def is_empty(self):
        return len(self.nodes) == 0

    def add_node(self, item):
        old_node = self.nodes.get(item.v_id)
        if old_node is None or item.g < old_node.g:
            self.nodes[item.v_id] = item              
            heappush(self.prioritized_queue, item)

    def get_best_node(self):
        best_node = heappop(self.prioritized_queue)
        v_id = best_node.v_id
        while self.nodes.pop(v_id, None) is None:
            best_node = heappop(self.prioritized_queue)
            v_id = best_node.v_id
        return best_node


class Closed:
    def __init__(self):
        self.elements = {}

    def __iter__(self):
        return iter(self.elements.values())
    
    def __len__(self):
        return len(self.elements)

    def add_node(self, item):
        self.elements[item.v_id] = item

    def was_expanded(self, item):
        return item.v_id in self.elements


def search(graph, start_id, goal_id, blocked, empty = None):
    # print("(shortest_path) Start. Vertices: ", start_id, goal_id)
    OPEN = Open()
    CLOSED = Closed()
    start_node = Node(start_id, 0, graph.get_euclidian_distance(start_id, goal_id) if empty is None else 0)
    OPEN.add_node(start_node)
    empty_result = []

    while not OPEN.is_empty():
        current_node = OPEN.get_best_node()
        # print("curr:", current_node.v_id)
        CLOSED.add_node(current_node)
        
        if empty is None:
            if current_node.v_id == goal_id:
                return True, current_node
        else:
            if current_node.v_id in empty:
                empty_result.append(current_node)
                empty.remove(current_node.v_id)
            if len(empty) == 0:
                return True, empty_result # TODO check minimum instantly 
        
        for neighbour_id in graph.get_neighbours(current_node.v_id):
            new_node = Node( neighbour_id)
            if neighbour_id in blocked:
                continue
            if (not CLOSED.was_expanded(new_node)) and (neighbour_id not in blocked):
                new_node.g = current_node.g + graph.get_euclidian_distance(current_node.v_id, neighbour_id)
                new_node.h = graph.get_euclidian_distance(neighbour_id, goal_id) if empty is None else 0
                new_node.F = new_node.g + new_node.h
                new_node.parent = current_node
                OPEN.add_node(new_node)
    if empty is None:
        return False, None
    else:
        if len(empty_result) == 0:
            return False, None
        else:
            return True, empty_result

def shortest_path(graph, start_id, goal_id, blocked):
    success, goal_node = search(graph, start_id, goal_id, blocked)
    if not success:
        return False, None
    return True, make_path(goal_node)

def path_to_closest_empty_vertex(graph, start_id, empty, blocked):
    new_empty = empty.copy()
    success, empty_nodes = search(graph, start_id, None, blocked, new_empty)
    if not success:
        return False, None
    node_empty_min = min(empty_nodes, key=lambda x : x.g)
    return True, make_path(node_empty_min)
    
def make_path(node):
    current = node
    path = []
    while current.parent:
        path.append(current.v_id)
        current = current.parent
    path.append(current.v_id)
    
    return path