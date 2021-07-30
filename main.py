import visualizer
from graph import Graph
import numpy as np

g = Graph()
g.add_vertex(0, np.array([0.0, 0.0]), [])
g.add_vertex(1, np.array([1.0, 0.0]), [])
g.add_vertex(2, np.array([1.0, 1.0]), [])
g.add_vertex(3, np.array([0.0, 1.0]), [])

visualizer.draw_graph(g)