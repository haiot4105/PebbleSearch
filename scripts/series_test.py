from single_test import single_test
from os import listdir
from os.path import isfile, join
import sys

def series_test(task_dir, timeout, result_log_path, redirect_output, save_log):
    result_log = open(result_log_path, 'w')
    for f in listdir(task_dir):
        if isfile(join(task_dir, f)) and f.endswith('.json'):
            task_path = join(task_dir, f)
            print("\nTask path:", task_path)
            n, s, v, e, rt, ft, ms = single_test(task_path, False, timeout, redirect_output, save_log)
            result_log.write(task_path + ' ' + str(n) +  ' ' + str(s) +  ' ' +  str(v) +  ' ' +  str(e) +  ' ' +  str(rt) + ' ' +  str(ft) + ' ' +  str(ms) + '\n')


def __main__():
    if len(sys.argv) < 3:
        print("Not enough command line arguments. Paths to tasks and result filename were expected")
        exit()
    task_dir = sys.argv[1]
    resfile = sys.argv[2]
    resfile = task_dir + resfile
    timeout_per_task = 30
    redirect_output = True
    save_log = False
    series_test(task_dir, timeout_per_task, resfile, redirect_output, save_log)


if __name__ == "__main__":
    __main__()






