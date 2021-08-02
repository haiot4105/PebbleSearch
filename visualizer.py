import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import time


fig = plt.figure()
fig.set_dpi(100)
fig.set_size_inches(7, 7)
ax = plt.axes(xlim=(-2, 7), ylim=(-2, 7))
anim = None

# def draw_graph(graph):
    # circles = []
    # for v in graph:
    #     circle = plt.Circle(graph.get_vertex_position(v), 0.08, color='b')
    #     ax.add_patch(circle)

    # for e in graph.get_edges():
    #     p1, p2 = graph.get_vertex_position(e[0]), graph.get_vertex_position(e[1])
    #     x = np.array([p1[0], p2[0]])
    #     y = np.array([p1[1], p2[1]])
    #     plt.plot(x, y, color='b')

    # plt.show()

curr_step = 0
curr_agent = 0

def draw(graph, starts, solution):
    global anim
    global curr_step
    global curr_agent
    global pos_from
    global pos_to
    global length
    global dt
    global dp
    global patch

    patches = dict()
    for agent, start in starts.items():
        print(agent, start)
        patches[agent] = plt.Circle(graph.get_vertex_position(start), 0.3, fc='r', zorder=10)

    curr_step = 0
    curr_agent = solution[curr_step][0]
    pos_from = graph.get_vertex_position(solution[curr_step][1]) 
    pos_to = graph.get_vertex_position(solution[curr_step][2])

    length = np.linalg.norm(pos_to - pos_from)
    dt = 0.1
    dp = (pos_to - pos_from)/length * dt


    patch = patches[curr_agent]

    def init():
        circles = []
        for v in graph:
            circle = plt.Circle(graph.get_vertex_position(v), 0.15, color='b')
            ax.add_patch(circle)

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
        global curr_agent
        global pos_from
        global pos_to
        global length
        global dt
        global dp
        global patch

        print(curr_agent)
        pos_to = graph.get_vertex_position(solution[curr_step][2])
        patch = patches[curr_agent]
        x, y = patch.center
        if np.linalg.norm(pos_to - np.array([x, y])) > dt:
            x += dp[0]
            y += dp[1]
            patch.center = (x, y)
        else:
            if curr_step + 1 < len(solution):
                curr_step += 1
            curr_agent = solution[curr_step][0]
            pos_from = graph.get_vertex_position(solution[curr_step][1]) 
            pos_to = graph.get_vertex_position(solution[curr_step][2])

            length = np.linalg.norm(pos_to - pos_from)
            dt = 0.1
            dp = (pos_to - pos_from)/length * dt
            patch = patches[curr_agent]

        return list(patches.values())

    anim = animation.FuncAnimation(fig, animate, 
                                init_func=init, 
                                frames=None, 
                                interval=5,
                                blit=True,
                                repeat=False )
    plt.show()
