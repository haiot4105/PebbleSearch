from single_test import single_test
from os import listdir
from os.path import isfile, join


def series_test(task_dir, timeout, result_log_path, redirect_output, save_log):
    result_log = open(result_log_path, 'w')
    for f in listdir(task_dir):
        if isfile(join(task_dir, f)) and f.endswith('.json'):
            task_path = join(task_dir, f)
            print("\nTask path:", task_path)
            n, s, v, e, rt, ft, ms = single_test(task_path, False, timeout, redirect_output, save_log)
            result_log.write(task_path + ' ' + str(n) +  ' ' + str(s) +  ' ' +  str(v) +  ' ' +  str(e) +  ' ' +  str(rt) + ' ' +  str(ft) + ' ' +  str(ms) + '\n')


def __main__():
    task_dir = "../tasks/40_small_graphs/json_5/"
    timeout_per_task = 30
    redirect_output = True
    save_log = False
    series_test(task_dir, timeout_per_task, "../tasks/result_5_tasks.txt", redirect_output, save_log)


if __name__ == "__main__":
    __main__()






