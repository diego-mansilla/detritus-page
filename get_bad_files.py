import os
from shutil import copyfile

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

DATASET_DIR = '../../DatasetSIPI'
DEST_DIR = 'app/static/bad_images'

detfiles = read_file('bad_files.txt')
print(len(detfiles))
detfiles = set(detfiles)
print(len(detfiles))
for subdir, dirs, files in os.walk(DATASET_DIR):
    for file in files:
        if(file.endswith('.png')):
            if (os.path.getsize(subdir+"/"+file) > 0):
                if get_file_name(file) in detfiles:
                    copyfile(subdir+"/"+file, DEST_DIR + "/" + file)