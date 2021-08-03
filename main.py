import visualizer
from graph import Graph
from push_and_swap import PushAndSwap
import numpy as np

g = Graph()
# g.add_vertex(0, np.array([0.0, 0.0]), {1, 3})
# g.add_vertex(1, np.array([5.0, 0.0]), {0, 2})
# g.add_vertex(2, np.array([2.5, 2.5]), {1, 3})
# g.add_vertex(3, np.array([0.0, 5.0]), {0, 2})
g.add_vertex( 0 , np.array([ -1.3673651084578786 , 2.2491687771793787 ]), { 7, 4, 2 })
g.add_vertex( 1 , np.array([ -3.698833413174707 , -3.1063663215782125 ]), { 5, 8, 2 })
g.add_vertex( 2 , np.array([ -2.6038433077966916 , -1.3307215448757348 ]), { 5, 8, 9 })
g.add_vertex( 3 , np.array([ 0.017826425750378405 , -4.218348331834337 ]), { 9, 6, 1 })
g.add_vertex( 4 , np.array([ 0.2604987027337753 , 0.222693918484258 ]), { 0, 6, 2 })
g.add_vertex( 5 , np.array([ -2.8007923517020994 , -2.0702802587520717 ]), { 2, 8, 1 })
g.add_vertex( 6 , np.array([ 1.229458332225617 , -2.3201592519562766 ]), { 3, 4, 0 })
g.add_vertex( 7 , np.array([ -2.804478366415962 , 2.149338326062855 ]), { 0, 2, 4 })
g.add_vertex( 8 , np.array([ -3.9913090144860295 , -1.5351973442965283 ]), { 5, 2, 1 })
g.add_vertex( 9 , np.array([ -1.5704839815950988 , -2.978981542285445 ]), { 5, 2, 3 })

a = [0, 1, 2, 3, 4]

s = {0 : 0, 1 : 1, 2 : 2, 3 : 3, 4 : 4}
t = {0 : 9, 1 : 3, 2 : 5, 3 : 6, 4 : 7}


solver = PushAndSwap(g, a, s, t )
success, solution = solver.solve()
print(success, solution)
visualizer.draw(g, s, solution)

