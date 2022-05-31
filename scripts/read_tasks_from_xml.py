import context
from utils import task_io
from single_test import single_test
from os import listdir
from os.path import isfile, join, splitext
from pebble_search.graph import Graph as Graph
from utils import visualizer




def get_first_n_agents_from_task(n, a, s, t):
    a_n = a[:n]
    s_n = dict()
    t_n = dict()
    print(a_n, s_n, t_n)
    for i in a_n:
        s_n[i] = s[i]
        t_n[i] = t[i]
    print(len(a_n), len(s_n), len(t_n))
    return a_n, s_n, t_n



def main():

    max_agents_num = 40
    min_agents_num = 2
    step_agents_num = 1
    
    task_num = 25
    task_dir = ""
    xml_task_dir = ""

    for i in range(task_num):
        print(xml_task_dir + str(i+1) +"_task.xml")
        positions, all_neighbours, a, s, t, size = task_io.read_task_from_xml(xml_task_dir + "map.xml", xml_task_dir + str(i+1) +"_task.xml")

        for n in range(min_agents_num, max_agents_num+1, step_agents_num):
            a_n, s_n, t_n = get_first_n_agents_from_task(n, a, s, t)
            task_io.save_task_to_json(task_dir + str(n) + '_' + str(i) +"_task.json", positions, all_neighbours, a_n, s_n, t_n, size)



if __name__ == "__main__":
    main()

