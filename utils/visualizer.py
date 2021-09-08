# TODO Optimization and refactoring are needed 

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import time


fig = plt.figure()
fig.set_dpi(100)
fig.set_size_inches(10, 10)
ax = plt.axes(xlim=(-6, 6), ylim=(-6, 6))
anim = None

curr_step = 0
curr_agent = 0
curr_step = 0
curr_substep = 0

curr_agent = 0
pos_from = 0
pos_to = 0

length = 0
substeps = 0
x_segm = 0
y_segm = 0
curr_segm = 0
dt = 0.1
patch = 0

def draw(graph, starts, solution):
    global anim
    global curr_step
    global curr_agent
    global pos_from
    global pos_to
    global length
    global dt
    global curr_substep
    global curr_segm
    global patch

    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=24, metadata=dict(artist='Me'), bitrate=2600)

    if solution is None:
        solution = [(0, starts[0], starts[0])]
    patches = dict()
    for agent, start in starts.items():
        patches[agent] = plt.Circle(graph.get_vertex_position(start), 0.4, fc='r', zorder=10)

    curr_step = 0
    curr_substep = 0
    
    curr_agent = solution[curr_step][0]
    pos_from = graph.get_vertex_position(solution[curr_step][1]) 
    pos_to = graph.get_vertex_position(solution[curr_step][2])
    
    length = np.linalg.norm(pos_to - pos_from)
    substeps = int(length/dt)
    x_segm = np.linspace(start=pos_from[0], stop=pos_to[0], num=substeps)
    y_segm = np.linspace(start=pos_from[1], stop=pos_to[1], num=substeps)
    curr_segm = np.vstack((x_segm, y_segm)).T
    dt = 0.1

    # length = np.linalg.norm(pos_to - pos_from)
    
    # dp = (pos_to - pos_from)/length * dt


    patch = patches[curr_agent]

    def init():
        circles = []
        for v in graph:
            circle = plt.Circle(graph.get_vertex_position(v), 0.15, color='b')
            ax.add_patch(circle)
            ax.text(*graph.get_vertex_position(v), str(v), fontweight='bold',zorder=10)

        for e in graph.get_edges():
            p1, p2 = graph.get_vertex_position(e[0]), graph.get_vertex_position(e[1])
            x = np.array([p1[0], p2[0]])
            y = np.array([p1[1], p2[1]])
            plt.plot(x, y, color='b')

        for a, p in patches.items():
            ax.add_patch(p)
        
        return list(patches.values())
    
    # init()
    def animate(i):
        global curr_step
        global curr_substep
        global curr_segm
        global curr_agent
        global pos_from
        global pos_to
        global dt
        global patch

        pos_to = graph.get_vertex_position(solution[curr_step][2])
        patch = patches[curr_agent]
        x, y = patch.center
        if curr_substep < len(curr_segm):
            x = curr_segm[curr_substep, 0]
            y = curr_segm[curr_substep, 1]
            patch.center = (x, y)
            curr_substep += 1
        else:
            if curr_step + 1 < len(solution):
                curr_step += 1
                curr_substep = 0
            else:
                curr_substep = len(curr_segm)-1
                
            curr_agent = solution[curr_step][0]
            
            
            # print(solution[curr_step][1], solution[curr_step][2], solution[curr_step][2] in graph.get_neighbours(solution[curr_step][1]))

            pos_from = graph.get_vertex_position(solution[curr_step][1]) 
            pos_to = graph.get_vertex_position(solution[curr_step][2])

            length = np.linalg.norm(pos_to - pos_from)
            substeps = int(length/dt)
            x_segm = np.linspace(start=pos_from[0], stop=pos_to[0], num=substeps)
            y_segm = np.linspace(start=pos_from[1], stop=pos_to[1], num=substeps)
            curr_segm = np.vstack((x_segm, y_segm)).T
            patch = patches[curr_agent]

        return list(patches.values())

    # anim = animation.FuncAnimation(fig, animate,
    #                             init_func=init,
    #                             frames=None,
    #                             interval=100,
    #                             blit=True,
    #                             repeat=False,
    #                             save_count=300)

    anim = animation.FuncAnimation(fig, animate,
                                init_func=init,
                                frames=None,
                                interval=100,
                                blit=False,
                                repeat=False)

    # anim.save("test.mp4", writer=writer)
    plt.show()
    print("Saved")