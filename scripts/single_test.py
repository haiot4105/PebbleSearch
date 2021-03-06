# TODO reading tasks from JSON files

import context
from pebble_search.size_push_and_rotate import PushAndRotateWithSizes
from pebble_search.size_push_and_rotate_base import SizePushAndRotateBase
# from pebble_search.push_and_rotate import PushAndRotate
from pebble_search.graph import Graph as Graph
# import utils.random_generator as random_generator
import utils.visualizer as visualizer
from utils import is_valid_solution
from utils import task_io
import multiprocessing
import time
import sys
import os
import traceback
from contextlib import redirect_stdout, redirect_stderr
import numpy as np


def __proccess_solver(g, a, s, t, r, redirect_output, save_log, file_path, ret_dict):
    success, solution = False, None
    runtime = 0
    try:
        log = sys.stdout 
        if redirect_output:
            if save_log:
                output_file = os.path.splitext(file_path)[0] + "log.txt"
                log = open(output_file, 'w')
            else:
                log = None
            
        with redirect_stdout(log):
            with redirect_stderr(log):
                
                solver = PushAndRotateWithSizes(g, a, s, t, r)
                # solver = SizePushAndRotateBase(g, a, s, t, r)
                # solver = PushAndRotate(g, a, s, t)
                start_time = time.time()
                success, solution = solver.solve()
                runtime = time.time() - start_time
    except:
        ret_dict['error'] = True
        traceback.print_exc()

    ret_dict['success'] = success
    ret_dict['solution'] = solution
    ret_dict['runtime'] = runtime


def compute_makespan_and_flowtime(solution, positions):
    makespan = 0.0
    flowtime = 0.0
    paths = dict()
    for agent, v_from, v_to in solution:
        if agent not in paths.keys():
            paths[agent] = 0.0
        curr_len = np.linalg.norm(positions[v_from] - positions[v_to])
        paths[agent] += curr_len
        flowtime += curr_len
    makespan = max(paths.values())
    return makespan, flowtime

def single_test(file_path, draw_res, timeout, redirect_output, save_log):
    positions, all_neighbours, a, s, t, r = task_io.read_task_from_json(file_path)

    g = Graph(positions, all_neighbours)
    solution = None
    valid = False
    success = False
    manager = multiprocessing.Manager()
    ret_dict = manager.dict()
    ret_dict['success'] = False
    ret_dict['solution'] = None
    ret_dict['error'] = False
    ret_dict['timeout'] = False
    ret_dict['runtime'] = 0

    output_file = os.devnull
    if redirect_output:
        if save_log:
            output_file = os.path.splitext(file_path)[0] + "log.txt"

    process = multiprocessing.Process(target=__proccess_solver, args=(g, a, s, t, r, redirect_output, save_log, file_path, ret_dict))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        # sys.stdout = os.
        ret_dict['error'] = True
        print("Timeout!")

    success = ret_dict['success']
    solution = ret_dict['solution']
    error = ret_dict['error']
    runtime = ret_dict['runtime']
    flowtime = 0
    makespan = 0

    

    if solution is not None:
        valid = is_valid_solution(g, a, s, t, solution, r)
        makespan, flowtime = compute_makespan_and_flowtime(solution, positions)
    print("Success:", success, "; Valid:", valid, "; Error:", error, "; Time:", runtime, "; Flowtime:", flowtime, "; Makespan:", makespan)

    if draw_res:
        visualizer.draw(g, s, solution)
    return len(a), success, valid, error, runtime, flowtime, makespan


def __main__():
    if len(sys.argv) < 2:
        print("Not enough command line arguments. Path to task was expected")
        exit()

    task_path = sys.argv[1]
    draw_task = False
    timeout = 300
    redirect_output = False
    save_log = False
    single_test(task_path, draw_task, timeout, redirect_output, save_log)


if __name__ == "__main__":
    __main__()
