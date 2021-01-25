#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import re
import os
import sys
import random
import shutil
import tempfile

try:
    import patoolib
except ImportError:
    print("Для для работы скрипта необходима библиотека patoolib и программа unrar")
    print("Чтобы установить patoolib наберите 'pip3 install patool'")
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
        print("Произошла ошибка считывания данных книг")
        quit();

def write_data(name, data):
    try:
        with open(name,'w', encoding='cp1251') as fout:
            fout.writelines(data)
    except Exception:
        print("Произошла ошибка записи данных книг")
        quit();

def create_file_list():
    files = []
    dirs = []
    for entry in os.scandir(path):
        if entry.name.startswith('BOOK_'):
            if entry.is_file() and entry.name.endswith(".lgk") and len(entry.name) == 12:
                files.append(entry.name)
            if entry.is_dir() and len(entry.name) == 8:
                dirs.append(entry.name)
    files.sort()
    dirs.sort()
    return [dirs, files]

def list_book():
    flist = create_file_list()
    if not (len(flist[0]) == 0):
        print("Список книг на карте:")
    else:
        print('Карта пуста')
    for indx, fname in enumerate(flist[1], 1):
        lines = read_data(fname)
        for s in lines:
            if (s.startswith("#Title=")):
                item_p2 = s[7:-1]
            if (s.startswith("#Author=")):
                item_p1 = s[8:-1]
        print(f"{indx}. {item_p1} - {item_p2}")

def remove_book(dlist):
    num_items = []
    flist = create_file_list()
    for item in dlist:
        if not (re.search('\d+\-\d+',item) == None):
            parts = item.split('-')
            num_items = num_items + [i for i in range(int(parts[0]), int(parts[1])+1)]
        elif (item.isdigit()):
            num_items.append(int(item))
        elif (item in ('a', 'all')):
            num_items = [i for i in range(1, len(flist[1])+1)]
    if (num_items == []):
        print('Укажите книги для удаления')
        quit();
    for num in num_items:
        if num >= 1 and num <= len(flist[1]):
            try:
                os.remove(flist[1][num-1])
                shutil.rmtree(flist[0][num-1] , ignore_errors=True)
            except Exception:
                print("Ошибка удаления книги")
        else:
            print(f"Такого номера книги не существует: {num}")

def clear_book():
    flist = create_file_list()
    flist1 = [felem[:8] for felem in flist[1]]
    dlist = [fdir for fdir in flist[0] if not (fdir in flist1)]
    if dlist != []:
        for d in dlist:
            shutil.rmtree(d , ignore_errors=True)
        print("Очищено")
    else:
        print("Очистка не требуется")

def add_book(alist):
    if len(alist) == 0:
        return
    tmp = tempfile.mkdtemp()
    for i in alist:
        flist = create_file_list()
        for te in range(1,1000):
            s = f"BOOK_{te:03d}"
            if not (s in flist[0]):
                break
        print(f"Распаковка книги {i}")
        patoolib.extract_archive(i,outdir=tmp,verbosity=-1)
        fname = f"{tmp}/BOOK_001.lgk"
        lines = read_data(fname)
        wlines = []
        for s1 in lines:
            if s1.startswith("BOOK_001"):
                s2 = s1.replace("BOOK_001",s)
            else:
                s2 = s1
            wlines.append(f"{s2[:len(s2)-1]}\r\n")
        write_data(fname, wlines)
        print("Копирование")
        shutil.move(f"{tmp}/BOOK_001/", f"{path}/{s}/")
        shutil.move(f"{tmp}/BOOK_001.lgk", f"{path}/{s}.lgk")
        print("Книга записана")
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
            print("Укажите файлы для добавления")
    elif (args[0] in ('delete', 'd')):
        if (n_args >= 2):
            remove_book(args[1:])
        else:
            print("Укажите книги для удаления")
    elif (args[0] in ('clear', 'c')):
        clear_book()
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
