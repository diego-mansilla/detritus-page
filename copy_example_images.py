import os
from shutil import copyfile
import ast

def load_dict_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return ast.literal_eval(data)

images = []
dir = '../../sipi/LRoot_sipi_v4'

def get_file_name(subdir):
    return subdir[subdir.rfind('/')+1:]

def read_file(filename):
    result = []
    with open(filename, 'r') as file:
        i = 0
        for line in file:
            i = i + 1
            if i == 1:
                continue
            result.append(get_file_name(line.strip()))
    return result

def get_class_name(path):
    parts = path.split('/')
    if len(parts) > 4:
        return parts[4]
    return None

from itertools import chain

def get_individual_values_set(data_map):
    return set(chain.from_iterable(data_map.values()))

DEST_DIR = 'app/static/images'
data_map = load_dict_from_file('incorrect_files_output.txt')

images = []
for subdir, dirs, files in os.walk(dir):
    for file in files:
        if file.endswith('.png'):
            if os.path.getsize(subdir + "/" + file) > 0:
                ff = subdir + "/" + file
                file_name = get_file_name(ff)
                class_name = get_class_name(ff)
                if file in get_individual_values_set(data_map):
                    dest_file_path = os.path.join(DEST_DIR, file)
                    if not os.path.exists(dest_file_path):
                        copyfile(subdir + "/" + file, dest_file_path)
                        print(f"Copied new file: {file}")