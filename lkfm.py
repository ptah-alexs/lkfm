#!/usr/bin/python3
# -*- coding: UTF-8 -*-
 
import os
import sys
import random
import argparse
import shutil
import tempfile

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    import patoolib
except ImportError:
    print("Для для работы скрипта необходима библиотека patoolib и программа unrar")
    print("Чтобы установить patoolib наберите 'pip3 install patool'")
    quit()

path = os.getcwd()
config_path = f'{os.path.expanduser("~")}/.local/share/lkfm.conf'
sec_global = "global"

#restFiles = [os.path.join(d[0], f) for d in os.walk(".") if not "_test" in d[0]
#             for f in d[2] if f.endswith(".rst")]

def createParser ():
    parser = argparse.ArgumentParser(prog="lkfm",
                                     description =''' Программа для управления аудиокнигами на картах памяти в формате LKF''',
                                     epilog ='''© ptah_alexs 2020. Автор программы, как всегда, не несет никакой ответственности ни за что.''', add_help = False)
    parent_group = parser.add_argument_group (title='Параметры')
    parent_group.add_argument ('--help', '-h', action='help', help='Справка')
    parent_group.add_argument('action', type=str, nargs='?', help='Доступны действия: list - Вывести список книг на карте; add - Добавить книгу на карту; delete - Удалить книгу с карты; clean - Очистить карту от не до конца удалённых книг.')
    parent_group.add_argument('file', type=str,nargs='*', help='Имя файла')
    return parser

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
    for indx, fname in enumerate(flist[1]):
        lines = read_data(fname)
        for s in lines:
            if (s.startswith("#Title=")):
                item_p2 = s[7:-1]
            if (s.startswith("#Author=")):
                item_p1 = s[8:-1]
        print(f"{indx}. {item_p1} - {item_p2}")

def remove_book(dlist):
    flist = create_file_list()
    for fnum in dlist:
        if str(fnum).isdigit():
            num = int(fnum)
            if num >= 1 and num <= len(flist[1]):
                try:
                    os.remove(flist[1][num-1])
                    shutil.rmtree(flist[0][num-1] , ignore_errors=True)
                except Exception:
                    print("Ошибка удаления книги")
            else:
                print(f"Такого номера книги не существует: {num}")
        else:
            print("Введите номер удаляемой книги")

def clean_book():
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
        print("Распаковка")
        patoolib.extract_archive(i,outdir=tmp)
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

def set_work_dir():
    config = configparser.ConfigParser()
    config.add_section(sec_global)
    config.set(sec_global, "work_dir", os.getcwd())
    try:
        with open(config_path, "w") as config_file:
            config.write(config_file)
    except Exception:
        print("Не могу записать конфигурационный файл")

def load_work_dir():
    global path
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
        except Exception:
            print("Не могу прочитать конфигурационный файл")
        if (config.has_section(sec_global)):
             if (config.has_option(sec_global,"work_dir")):
                 path = config.get(sec_global, "work_dir")

def clear_config():
    if os.path.exists(config_path):
        os.remove(config_path)

def main():
    if (len(sys.argv)  < 2 ):
        parser.print_help()
        quit()
    load_work_dir()
    if (args.action == "add"):
        if (len(sys.argv) > 2):
            add_book(args.file)
        else:
            print("Укажите файлы для добавления")
    elif (args.action == "delete"):
        if (len(sys.argv) > 2):
            remove_book(args.file)
        else:
            print("Укажите книги для удаления")
    elif (args.action == "list"):
        print("Список книг на карте:")
        list_book()
    elif (args.action == "clean"):
        clean_book()
    elif (args.action == "work-dir"):
        set_work_dir()
    elif (args.action == "clear-config"):
        clear_config()
    else:
        parser.print_help()

if __name__ == "__main__":
    parser = createParser()
    args = parser.parse_args(sys.argv[1:])
    main()
