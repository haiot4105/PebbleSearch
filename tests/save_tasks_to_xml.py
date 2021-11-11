import context
from utils import task_io
from single_test import single_test
from os import listdir
from os.path import isfile, join, splitext


def save_tasks_to_xml(task_dir, output_dir):
    for task_file in listdir(task_dir):
        if isfile(join(task_dir, task_file)) and task_file.endswith('.json'):
            task_path = join(task_dir, task_file)
            output_files = join(output_dir, splitext(task_file)[0]) 

            print("\nTask:", task_path, "output", output_files)
            task_io.save_task_to_xml(output_files, *task_io.read_task_from_json(task_path))
            # n, s, v, e = single_test(task_path, False, timeout, redirect_output, save_log)
            # result_log.write(task_path + ' ' + str(n) +  ' ' + str(s) +  ' ' +  str(v) +  ' ' +  str(e) +  '\n')


def __main__():
    # task_dir = "../tasks/"
    # output_dir = "../tasks/xml/"
    # save_tasks_to_xml(task_dir, output_dir)
    task_io.save_task_to_xml("../tasks/xml/9_14_task", *task_io.read_task_from_json("../tasks/9_14_task.json"))


if __name__ == "__main__":
    __main__()
