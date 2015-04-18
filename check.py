#!/usr/bin/python

__author__ = 'Jungsik Choi'

import os
import re
import time
import subprocess


def get_cur_time():
    now = time.localtime()
    s = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, 
            now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    return str(s)


def execute(_cmd):
    msg = '  [' + get_cur_time() + ' execute] ' + _cmd
    print msg

    fd = subprocess.Popen(_cmd, shell=True,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
    stdout, stderr = fd.communicate()
    return stdout, stderr


def unzip(file_name):
    extention = os.path.splitext(file_name)[1]
    option = ''
    if extention == '.tar':
        option = 'xf'
    elif extention == '.gz':
        option = 'xzf'
    else:
        print '[Exception] Unexpected file name'

    re_compile = re.compile(r'^(\d){10}')
    re_match = re_compile.match(file_name)
    student_id = re_match.group()
    
    cmd = 'mkdir ' + student_id
    execute(cmd)

    cmd = 'tar ' + option + ' submission/' + file_name + ' -C ' + student_id
    execute(cmd)
    return student_id


def compile(path):
    ready = False

    os.chdir(path)
    while True:
        file_list = os.listdir(os.getcwd())
        dir_list = []
        path = None

        for file_name in file_list:
            re_com = re.compile('^makefile$', re.I)
            if bool(re_com.findall(file_name)):
                ready = True
                stdout, stderr = execute('make')
                print stdout
                return os.getcwd()

            elif os.path.isdir(file_name):
                dir_list.append(file_name)

        if not ready:
            for dir_name in dir_list:
                path = compile(dir_name)
                if not path == None:
                    return path
        else:
            return path


def get_elapsed_time(_result):
    expression = '\d+\.\d+user\s+\d+\.\d+system'
    expression += '\s+((?P<hour>\d+)\:)?'
    expression += '(?P<minute>\d+):'
    expression += '(?P<second>\d+(\.\d+)?)elapsed\s'
    re_compile = re.compile(expression)

    result = _result.strip()
    time_result = result.replace('\n', ' ')
    re_search = re_compile.search(time_result)

    if re_search.group('hour') == None:
        hour = 0
    else:
        hour = float(re_search.group('hour'))
    minute = float(re_search.group('minute'))
    second = float(re_search.group('second'))

    elapsed_time = (hour * 60 * 60) + (minute * 60) + second
    return elapsed_time

    
def first_offset(test_file):
    while True:
        line = test_file.readline()
        if not line:
            break
        if bool(re.search(r'^\s*\#\s*\d+', line)):
            break


def next_list(_testfile, _n):
    list = []

    first_offset(_testfile)
    for i in range(1, _n+1):
        line = _testfile.readline()
        if not line:
            list.append('EOF')
            break
        line = line.replace(',', '')
        line = line.replace(' ', '')
        line = line.strip()
        line = str(i) + line
        list.append(line)


    return list
def get_nr_solutions(_testfile):
    nr_solutions = 0
    lines = _testfile.readlines()
    expression = '^\s*\#\s*(?P<number>\d+)'
    re_compile = re.compile(expression)

    for line in lines:
        re_match = re_compile.match(line)
        if re_match:
            nr_solutions = int(re_match.group('number'))
    _testfile.seek(0, os.SEEK_SET)
    return nr_solutions


def accuracy_test(_sol_path, _n):
    total_count = 0

    if _n == 8:
        answer_file = open(_sol_path + '/solution-8', 'r')
        candidate_file = open('result-8.out', 'r')
    elif _n == 11:
        answer_file = open(_sol_path + '/solution-11', 'r')
        candidate_file = open('result-11.out', 'r')
    elif _n == 13:
        answer_file = open(_sol_path + '/solution-13', 'r')
        candidate_file = open('result-13.out', 'r')
    elif _n == 17:
        answer_file = open(_sol_path + '/solution-17', 'r')
        candidate_file = open('result-17.out', 'r')
    else:
        print '  [accuracy_test] unexpected N'
        return False

    nr_solutions = get_nr_solutions(answer_file)

    msg = '  [' + get_cur_time() + ' accuracy_test] ' + str(_n) 
    msg += ', nr_solutions=' + str(nr_solutions)
    print msg

    while True:
        answer_list = next_list(answer_file, _n)

        if answer_list[0] == 'EOF':
            break

        candidate_file.seek(0, os.SEEK_SET)

        while True:
            candidate_list = next_list(candidate_file, _n)

            if candidate_list[0] == 'EOF':
                break

            if not len(candidate_list) == _n:
                msg = '  [' + get_cur_time() + ' accuracy_test] '
                msg += 'Accuracy Test Fail, len(candidate_list) != N'
                print msg
                return False

            cnt = 0
            for j in range(0, _n):
                if answer_list[j] == candidate_list[j]:
                    cnt = cnt + 1
            if cnt == _n:
                total_count = total_count + 1

    answer_file.close()
    candidate_file.close()

    if total_count == nr_solutions:
        msg = '  [' + get_cur_time() + ' accuracy_test] '
        msg += 'Accuracy Test Success'
        print msg
        return 1
    else:
        msg = '  [' + get_cur_time() + ' accuracy_test] '
        msg += 'Accuracy Test Fail'
        print msg
        return 0

def run(id, path, result_file, sol_path):
    os.chdir(path)

    # N=8
    cmd = 'time ./nqueens 8 > result-8.out'
    std_out, std_err = execute(cmd)
    time1 = get_elapsed_time(std_err)
    print '\ttime1 = ' + str(time1)
    accuracy1 = accuracy_test(sol_path, 8)

    # N=11
    cmd = 'time ./nqueens 11 > result-11.out'
    std_out, std_err = execute(cmd)
    time2 = get_elapsed_time(std_err)
    print '\ttime2 = ' + str(time2)
    accuracy2 = accuracy_test(sol_path, 11)

    # N=13
    cmd = 'time ./nqueens 13 > result-13.out'
    std_out, std_err = execute(cmd)
    time3 = get_elapsed_time(std_err)
    print '\ttime3 = ' + str(time3)
    accuracy3 = accuracy_test(sol_path, 13)

    """
    # N=17
    cmd = 'time ./nqueens 17 > result-17.out'
    std_out, std_err = execute(cmd)
    time4 = get_elapsed_time(std_err)
    print '\ttime4 = ' + str(time4)
    accuracy4 = accuracy_test(sol_path, 17)
    """

    msg = '"' + str(id) + '"\t' + str(accuracy1) + '\t' + str(time1) + '\t'
    msg += str(accuracy2) + '\t' + str(time2) + '\t'
    msg += str(accuracy3) + '\t' + str(time3) + '\n'
    result_file.write(msg)



def main():
    result_file = open('result.csv', 'w')
    result_file.write('"ID"\t"Accuracy1"\t"Time1"\t"Accuracy2"\t"Time2"\t"Accuracy3"\t"Time3"\n')
    cur_path = os.getcwd()
    sol_path = cur_path + '/solutions'
    directory = 'submission'
    files = os.listdir(directory)
    nr_works = len(files)

    for file_name in files:
        print '\n========== (' + str(nr_works) + ') ' + file_name + ' =========='
        student_id = unzip(file_name)
        path = compile(student_id)
        run(student_id, path, result_file, sol_path)
        os.chdir(cur_path)
        nr_works = nr_works - 1

    result_file.close()
            

if __name__ == '__main__':
    main()
