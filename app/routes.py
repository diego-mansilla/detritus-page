import os
from flask import render_template
from app import app

DEST_DIR = 'static/images'

def get_file_name(subdir):
    return subdir[subdir.rfind('/')+1:]

def get_class_name(path):
    parent_dir_path = os.path.dirname(path)
    parent_dir_name = os.path.basename(parent_dir_path)
    return parent_dir_name

def read_file(filename):
    result = []
    labels = []
    with open(filename, 'r') as file:
        i = 0
        for line in file:
            i = i + 1
            if i == 1:
                continue
            result.append(get_file_name(line.strip()))
            labels.append(get_class_name(line.strip()))
    return result, labels

@app.route('/')
def home():
    images_input , labels = read_file('input.txt')
    images = ['images/' + img for img in images_input]
    print(images)
    return render_template('home.html', images=images, labels=labels)
