#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re
import os
import sys
import random
import shutil
import tempfile
import subprocess

try:
    import patoolib
except ImportError:
    print('Для для работы скрипта необходима библиотека patoolib и программа unrar')
    print('Чтобы установить patoolib наберите \'pip3 install patool\'')
    quit()

#TODO Сделать запаковку книг с карты в архивы
#TODO Избавиться от patoolib

path = os.getcwd()
config_path = f'{os.path.expanduser("~")}/.local/share/lkfm.conf'

#restFiles = [os.path.join(d[0], f) for d in os.walk(".") if not "_test" in d[0]
#             for f in d[2] if f.endswith(".rst")]

def print_help():
    print('LKFM - программа для управления аудиокнигами на картах памяти в формате LKF')
    print('')
    print('lkfm [-h, --help] действие [файл, ...]')
    print('')
    print('-h, --help - Вывести справку')
    print('')
    print('действие - Доступны действия: list, add, delete, clear, work-dir, clear-config:')
    print('help, h            - Вывести справку;')
    print('list, l            - Вывести список книг на карте;')
    print('add, a             - Добавить книгу на карту;')
    print('delete, d          - Удалить книгу с карты;')
    print('pack, p            - Упаковать книгу с карты')
    print('clear, c           - Очистить карту от не до конца удалённых книг;')
    print('set-work-dir, sd   - Установить целевой каталог для записи книг;')
    print('unset-work-dir, ud - Очистить настройки;')
    print('')
    print('файл - Файл книги')
    print('')
    print('© ptah_alexs 2020. Автор программы, как всегда, не несет никакой ответственности ни за что.')
    quit()

def read_data(name):
    try:
        with open(name,'r', encoding='cp1251') as fin:
            return fin.readlines()
    except Exception:
        print('Произошла ошибка считывания данных книг')
        quit();

def write_data(name, data):
    try:
        with open(name,'w', encoding='cp1251') as fout:
            fout.writelines(data)
    except Exception:
        print('Произошла ошибка записи данных книг')
        quit();

def create_file_list():
    files = []
    dirs = []
    for entry in os.scandir(path):
        if entry.name.startswith('BOOK_'):
            if entry.is_file() and entry.name.endswith('.lgk') and len(entry.name) == 12:
                files.append(entry.name)
            if entry.is_dir() and len(entry.name) == 8:
                dirs.append(entry.name)
    files.sort()
    dirs.sort()
    return [dirs, files]

def list_book():
    flist = create_file_list()
    if not (len(flist[0]) == 0):
        print('Список книг на карте:')
    else:
        print('Карта пуста')
    for indx, fname in enumerate(flist[1], 1):
        lines = read_data(f'{path}/{fname}')
        for s in lines:
            if (s.startswith('#Title=')):
                item_p2 = s[7:-1]
            if (s.startswith('#Author=')):
                item_p1 = s[8:-1]
        print(f"{indx}. {item_p1} - {item_p2}")

def parse_num_args(nlist, flist):
    num_items = []
    for item in nlist:
        if not (re.search('\d+\-\d+',item) == None):
            parts = item.split('-')
            num_items = num_items + [i for i in range(int(parts[0]), int(parts[1])+1)]
        elif (item.isdigit()):
            num_items.append(int(item))
        elif (item in ('a', 'all')):
            num_items = [i for i in range(1, len(flist[1])+1)]
    return num_items

def remove_book(dlist):
    flist = create_file_list()
    num_items = parse_num_args(dlist, flist)
    if (num_items == []):
        print('Укажите книги для удаления')
        quit();
    for num in num_items:
        if num >= 1 and num <= len(flist[1]):
            try:
                os.remove(f'{path}/{flist[1][num-1]}')
                shutil.rmtree(f'{path}/{flist[0][num-1]}', ignore_errors=True)
            except Exception:
                print('Ошибка удаления книги')
        else:
            print(f'Такого номера книги не существует: {num}')

def pack_book(plist):
    flist = create_file_list()
    num_items = parse_num_args(plist, flist)
    if (num_items == []):
        print('Укажите книги для упаковки')
        quit();
    tmp = tempfile.mkdtemp()
    for num in num_items:
        if num >= 1 and num <= len(flist[1]):
            b_path = f'{tmp}/{num:03}'
            bf_path = f'{b_path}/BOOK_001'
            bl_path = f'{b_path}/BOOK_001.lgk'
            print('Копирование')
            try:
                shutil.copytree(f'{path}/{flist[0][num-1]}', bf_path)
                shutil.copy2(f'{path}/{flist[1][num-1]}',bl_path)
            except Exception:
                print(f'Ошибка копирования книги {num}')
            lines = read_data(bl_path)
            for n, s1 in enumerate(lines):
                if (s1.startswith('#Title=')):
                    item_p2 = s1[7:-1]
                if (s1.startswith('#Author=')):
                    item_p1 = s1[8:-1]
                lines[n] = s1.replace(f'BOOK_{num:03}','BOOK_001')
            write_data(bl_path,lines)
            a_path = f'{tmp}/{item_p1} - {item_p2}.rar'
            print('Упаковка')
            try:
                retcode = subprocess.call(f'/usr/bin/rar a -r -m5 -- \"{a_path}\" BOOK_001.lgk BOOK_001/ > /dev/null',cwd = b_path, shell=True)
                if retcode < 0:
                    print("Процесс прерван сигналом: ", -retcode, file=sys.stderr)
            except OSError as e:
                print("Выполнение невозможно: ", e, file=sys.stderr)
                shutil.rmtree(tmp , ignore_errors=True)
                quit()
            shutil.move(a_path, os.getcwd())
            print(f'Книга {item_p1} - {item_p2} упакована')
        else:
            print(f'Такого номера книги не существует: {num}')
    shutil.rmtree(tmp , ignore_errors=True)

def clear_book():
    flist = create_file_list()
    flist1 = [felem[:8] for felem in flist[1]]
    dlist = [fdir for fdir in flist[0] if not (fdir in flist1)]
    if dlist != []:
        for d in dlist:
            shutil.rmtree(f'{path}/{d}' , ignore_errors=True)
        print('Очищено')
    else:
        print('Очистка не требуется')

def add_book(alist):
    if len(alist) == 0:
        return
    tmp = tempfile.mkdtemp()
    for i in alist:
        flist = create_file_list()
        for te in range(1,1000):
            s = f'BOOK_{te:03d}'
            if not (s in flist[0]):
                break
        print(f'Распаковка книги {i}')
        patoolib.extract_archive(i,outdir=tmp,verbosity=-1)
        fname = f'{tmp}/BOOK_001.lgk'
        lines = read_data(fname)
        wlines = []
        for s1 in lines:
            if s1.startswith('BOOK_001'):
                s2 = s1.replace('BOOK_001',s)
            else:
                s2 = s1
            wlines.append(f'{s2[:len(s2)-1]}\r\n')
        write_data(fname, wlines)
        print('Копирование')
        shutil.move(f'{tmp}/BOOK_001/', f'{path}/{s}/')
        shutil.move(f'{tmp}/BOOK_001.lgk', f'{path}/{s}.lgk')
        print('Книга записана')
    shutil.rmtree(tmp , ignore_errors=True)

def set_work_dir(path):
    write_data(config_path, path)
    print('Целевой каталог записан')

def load_work_dir():
    global path
    if os.path.exists(config_path):
        conf = read_data(config_path)
        path = conf[0]

def unset_work_dir():
    if os.path.exists(config_path):
        os.remove(config_path)
        print('Настройки целевого каталога удалены')

def main():
    args = sys.argv[1:]
    n_args = len(args)
    load_work_dir()
    if (n_args == 0):
        print_help()
    if (args[0] in ('-h', '--help', 'help','h')):
        print_help()
    elif (args[0] in ('list', 'l')):
        list_book()
    elif (args[0] in ('add', 'a')):
        if (n_args >= 2):
            add_book(args[1:])
        else:
            print('Укажите файлы для добавления')
    elif (args[0] in ('delete', 'd')):
        if (n_args >= 2):
            remove_book(args[1:])
        else:
            print('Укажите книги для удаления')
    elif (args[0] in ('clear', 'c')):
        clear_book()
    elif (args[0] in ('pack', 'p')):
        if (n_args >= 2):
            pack_book(args[1:])
        else:
            print('Укажите книги для упаковки')
    elif (args[0] in ('set-work-dir', 'sd')):
        if (n_args >= 2):
            set_work_dir(args[1])
        else:
            set_work_dir(os.getcwd())
    elif (args[0] in ('unset-work-dir', 'ud')):
        unset_work_dir()
    else:
        print('Неизвестная команда.\n')
        print_help()

if __name__ == "__main__":
    main()
