import os
import pickle


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

images = []
file_name_class_map = {}
confusion_matrix = {}
for subdir, dirs, files in os.walk(dir):
    for file in files:
        if(file.endswith('.png')):
            if (os.path.getsize(subdir+"/"+file) > 0):
                ff = subdir+"/"+file
                file_name = get_file_name(ff)
                class_name = get_class_name(ff)
                file_name_class_map[file_name] = class_name

with open('file_name_class_map.txt', 'wb') as file:
    pickle.dump(file_name_class_map, file)