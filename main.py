import visualizer
from graph import Graph
from push_and_swap import PushAndSwap
import numpy as np

g = Graph()
g.add_vertex(0, np.array([0.0, 0.0]), {1, 3})
g.add_vertex(1, np.array([5.0, 0.0]), {0, 2})
g.add_vertex(2, np.array([2.5, 2.5]), {1, 3})
g.add_vertex(3, np.array([0.0, 5.0]), {0, 2})

a = [0, 1]

s = {0 : 0, 1 : 1}
t = {0 : 2, 1 : 3}


solver = PushAndSwap(g, a, s, t )
success, solution = solver.solve()
print(success, solution)
visualizer.draw(g, s, solution)
# visualizer.draw_graph(g)

# visualizer.test(g)
