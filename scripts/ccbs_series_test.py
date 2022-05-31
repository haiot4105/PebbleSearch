from os import listdir
from os.path import isfile, join, splitext
import subprocess
import re
import sys
TIMEOUT = 30

def series_test(task_dir, result_log_path, config_path, bin_path):
    result_log = open(result_log_path, 'w')
    for f in listdir(task_dir):
        if isfile(join(task_dir, f)) and f.endswith('task.xml'):
            task_path = join(task_dir, f)
            print(task_path, "Start")
            map_path = splitext(task_path)[0] + "_map.xml"
            # config_path = join(task_dir, "config.xml")
            number_of_agents_str = f.split('_')[0]
            if bin_path[0:1] != './':
                bin_path = './' + bin_path
            s, v, e = False, False, False
            try:
                result = subprocess.run([bin_path, map_path, task_path, config_path], stdout=subprocess.PIPE, timeout=TIMEOUT)
                s, v, e = parse_result(str(result.stdout))
            except subprocess.TimeoutExpired:
                s, v, e = False, False, False
            except Exception as e:
                print(e)
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
    if len(sys.argv) < 3:
        print("Not enough command line arguments. Paths to binary and to config file were expected")
        exit()
    task_dir = "../tasks/40_small_graphs/xml_7/"
    print("Bin file", sys.argv[1])
    print("Config file", sys.argv[2])
    bin_file = sys.argv[1]
    config_file = sys.argv[2]
    result_log_file = splitext(config_file)[0] + "_result.txt"
    print("Config file", result_log_file)
    series_test(task_dir, result_log_file, config_file, bin_file)


if __name__ == "__main__":
    __main__()