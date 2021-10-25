import os, re
from pathlib import Path

my_file = open("report.txt", "w")    # файл для хранения резельтатов выполнения условий

# функция для проверки, что папки ft_run и ft_reference существуют
def first_condition (name):
    if len(os.listdir(name)) == 0:
        my_file.write("FAIL  " + str(name)+"\n")
        my_file.write("directory missing: ft_reference\n")
        my_file.write("directory missing: ft_run\n")
        return False
    elif len(os.listdir(name)) == 1:
        t = os.listdir(name)
        my_file.write("FAIL  "+str(name)+"\n")
        if 'ft_reference' not in t[0]:
            my_file.write("directory missing: ft_reference\n")
        if 'ft_run' not in t[0]:
            my_file.write("directory missing: ft_run\n")
        return False
    else:
        return True

# функция для проверки, что в папках ft_run и ft_reference совпадает набор файлов "*.stdout".
def second_condition (lst):
    ft_ref, ft_run = [], []       # для распределения путей
    set_ref, set_run = [], []     # для операций над множествами
    for i in lst:
        if "ft_reference" in i:
            ft_ref.append(i)
            t = ''.join(i[-1])
            if t:
                set_ref.append(t)
        if "ft_run" in i:
            ft_run.append(i)
            t = ''.join(i[-1])
            if t:
                set_run.append(t)
    set_run = set(set_run)
    set_ref = set(set_ref)
    if set_run == set_ref:
        temp = third_condition(ft_run)
        fourth_condition(ft_ref, ft_run, temp)
    else:
        my_file.write("FAIL  "+str(lst[0][34:lst[0].find('ft_'):])+"\n")
        if set_ref-set_run:
            my_file.write(f"In ft_run there are missing files present in ft_reference:"
                          f" {''.join([i+ '.stdout ' for i in set_ref-set_run])}\n")
        if set_run-set_ref:
            my_file.write(f"In ft_run there are extra files not present in ft_reference:"
                          f" {''.join([i+ '.stdout ' for i in set_run-set_ref])}\n")
        return False

# функция для проверки отсутствия в папках ft_run слова "error" и наличие строки "Solver finished at"
def third_condition (ft_run):
    interim = True          # имя файла выводилось 1 раз
    for i in ft_run:
        temp = i
        t = os.listdir(i)
        for j in t:
            i = os.path.join(i, j)
            if ".stdout" in str(i):
                with open(i, 'r') as f:
                    count = 0
                    text = ''
                    interim = True
                    for line in f.readlines():
                        count += 1
                        text += line
                        if "error" in line.lower():
                            if interim:
                                my_file.write("FAIL  "+str(i[34:i.find('ft_'):])+"\n")
                                interim = False
                            my_file.write(f"{i[-10::]}({count}), {line[:-1:]}\n")
                    if text[text.find(r"Solver finished at")-1]!='\n':
                        if interim:
                            my_file.write("FAIL  "+str(i[34:i.find('ft_'):])+f"\n{i[-10::]}: missing 'Solver finished at'\n")
                            interim = False
            i = temp
    return interim

# вспомогательня функция для 4 условия, максимального и Total чисел
def auxiliary_for_four(name):
    with open(name, 'r') as f:
        text = f.read()
        match = [float(i) for i in re.findall(r"Memory Working Set Current = .* Mb, Memory Working Set Peak = (\d+.\d+) Mb", text)]
        total = [int(i) for i in re.findall(r"MESH::Bricks: Total=(\d+) Gas=.*Solid=.* Partial=.* Irregular=.*", text)]
    return [max(match), total[-1]]

# функция для сравнения результатов ft_reference и ft_run
def fourth_condition(ft_reference, ft_run, z):
    pr = True
    _ref, _run = [], []
    total_ref, total_run = 0, 0
    count = -1
    for i, j in zip(ft_reference, ft_run):
        temp = [i, j]
        ti = os.listdir(i)
        tj = os.listdir(j)
        for k, m in zip(ti, tj):
            i = os.path.join(i, k)
            j = os.path.join(j, m)
            if ".stdout" in str(i) and ".stdout" in str(j):
                interim_i, interim_j = auxiliary_for_four(i), auxiliary_for_four(j)
                total_ref, total_run = interim_i[1], interim_j[1]
                _ref.append(interim_i[0])
                _run.append(interim_j[0])
            i, j = temp[0], temp[1]
        count += 1
        if (abs(total_run/total_ref - 1)) > 0.1:
            if z:
                my_file.write("Fail "+str(ft_run[0][34:ft_run[0].find('ft_'):])+"\n")
            my_file.write(f"{''.join(os.listdir(ft_run[count]))}:  "
                          f"different 'Total' of bricks (ft_run={total_run}, ft_reference={total_ref}, "
                          f"rel.diff={round(total_run/total_ref - 1, 2)}, criterion=0.1)\n")
            pr = False
    count = -1
    for i, j in zip(_ref, _run):
        count += 1
        if (abs(i/j-1)) > 0.5:
            if z:
                my_file.write("Fail  "+str(ft_run[0][34:ft_run[0].find('ft_'):])+'\n')
            my_file.write(f"{''.join(os.listdir(ft_run[count]))}: "
                  f"different 'Memory Working Set Peak' (ft_run={j}, ft_reference={i}, "
                  f"rel.diff={abs(round(j/i-1, 2))}, criterion=0.5)\n")
            pr = False
    if pr and z:
        my_file.write("OK  "+str(ft_run[0][34:ft_run[0].find('ft_'):])+'\n')

tow = []   # список для хранения путей к файлам или каталогам из одной дириктории

# функция для распределения путей к файлам или каталогам, лежащим в одной директории
def distribution(name, dir = ''):
    if len(tow) == 0:
        tow.append(str(name))
    elif name == 'last':
        t = second_condition(tow)
        tow.clear()
        return t
    elif dir in str(tow[0]):
        tow.append(str(name))
    else:
        t = second_condition(tow)
        tow.clear()
        tow.append(str(name))
        return t

# функция для обхода путей к файлам и каталогам
def traversing_path (target_path, level=0, dir = ''):

    # проверка путей на заданные условия
    def inner_check(folder, level, dir=''):
        if level == 2:
            return first_condition(target_path)
        if level == 5 and dir in str(target_path):
            return distribution(target_path, dir)
        return True

    t = inner_check(target_path.name, level, dir)
    for file in target_path.iterdir():
        if file.is_dir() and t == True:
            if level == 2:
                dir = target_path.name
            traversing_path(file, level+1, dir)
        else:
            inner_check(file.name, level+1, dir)


path = Path(r'C:\Users\acer\Downloads\task1\logs')    # путь к каталогу
traversing_path(path)                                 # обход данного каталога
if len(tow) >= 1:
    distribution('last')
my_file.close()