import context
from utils import task_io
from single_test import single_test
from os import listdir
from os.path import isfile, join, splitext
from pebble_search.graph import Graph as Graph
from utils import visualizer
import os

result_dir = ""

task_num = 40
number_of_agents = 5

count = 0
for i in range(task_num):
    result_file = result_dir + str(number_of_agents) + "_" + str(i) + "_task_log.xml"
    
    if(os.path.isfile(result_file)):
        print(i, task_io.read_xml_ccbs_results(result_file)[0])
        count += 1
    else:
        print(i, 0)
print(count)