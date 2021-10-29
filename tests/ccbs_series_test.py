from os import listdir
from os.path import isfile, join, splitext
import subprocess
import re


def series_test(task_dir, result_log_path):
    result_log = open(result_log_path, 'w')
    for f in listdir(task_dir):
        if isfile(join(task_dir, f)) and f.endswith('task.xml'):
            task_path = join(task_dir, f)
            map_path = splitext(task_path)[0] + "_map.xml"
            config_path = join(task_dir, "config.xml")
            number_of_agents_str = f.split('_')[0]
            
            s, v, e = False, False, False
            try:
                result = subprocess.run(['./CCBS', map_path, task_path, config_path], stdout=subprocess.PIPE, timeout=30)
                s, v, e = parse_result(str(result.stdout))
            except subprocess.TimeoutExpired:
                s, v, e = False, False, False
            except:
                print("\nEnd\n")
                exit(-1)
            summary = task_path + ' ' + number_of_agents_str +  ' ' + str(s) +  ' ' +  str(v) +  ' ' +  str(e) +  '\n'
            print(summary)
            result_log.write(summary)


def parse_result(ccbs_res):
    s = False
    v = False
    e = False
    if re.search('Soulution found: true', ccbs_res):
        s = True
        v = True
    elif re.search('Soulution found: false', ccbs_res):
        s = False
    else:
        e = True
    return s, v, e


def __main__():
    task_dir = "../tasks/xml/"

    series_test(task_dir, "../tasks/xml/result.txt")


if __name__ == "__main__":
    __main__()