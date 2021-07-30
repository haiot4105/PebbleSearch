import matplotlib.pyplot as plt

def draw_graph(graph):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    circles = []
    for v in graph:
        circle = plt.Circle(graph.get_vertex_position(v), 0.1, color='b')
        # circles.append()
        ax.add_patch(circle)

    plt.show()