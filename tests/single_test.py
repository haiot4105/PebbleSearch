# TODO reading tasks from JSON files

import context
from pebble_search.size_push_and_rotate import PushAndRotateWithSizes
from pebble_search.graph import Graph as Graph
import utils.random_generator as random_generator
import utils.visualizer as visualizer
from utils import is_valid_solution
from utils import task_json_io
import multiprocessing
import time
import sys
import os
import traceback
from contextlib import redirect_stdout, redirect_stderr


def __proccess_solver(g, a, s, t, r, ret_dict):
    success, solution = False, None
    try:
        solver = PushAndRotateWithSizes(g, a, s, t, r)
        success, solution = solver.solve()
    except:
        ret_dict['error'] = True
        traceback.print_exc()

    ret_dict['success'] = success
    ret_dict['solution'] = solution


def single_test(file_path, draw_res, timeout, redirect_output, save_log):
    positions, all_neighbours, a, s, t, r = task_json_io.read_task_from_json(file_path)

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

    output_file = os.devnull
    if redirect_output:
        if save_log:
            output_file = os.path.splitext(file_path)[0] + "log.txt"


    process = multiprocessing.Process(target=__proccess_solver, args=(g, a, s, t, r, ret_dict))
    if redirect_output:
        with open(output_file, 'w') as log:
            with redirect_stdout(log):
                with redirect_stderr(log):
                    process.start()
                    process.join(timeout)
    else:
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
    if solution is not None:
        valid = is_valid_solution(g, a, s, t, solution, r)
    print("Success:", success, "; Valid:", valid, "; Error:", error)

    if draw_res:
        visualizer.draw(g, s, solution)
    return len(a), success, valid, error


def __main__():
    task_path = "../tasks/11_2_task.json"
    draw_task = False
    timeout = 30
    redirect_output = False
    save_log = False
    single_test(task_path, draw_task, timeout, redirect_output, save_log)


if __name__ == "__main__":
    __main__()
