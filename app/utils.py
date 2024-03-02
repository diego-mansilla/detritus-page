import os

def get_file_name(subdir):
    return subdir[subdir.rfind('/')+1:]

def get_class_name(path):
    parent_dir_path = os.path.dirname(path)
    parent_dir_name = os.path.basename(parent_dir_path)
    if parent_dir_name == "Detritus":
        return "Non Plankton"
    return "Plankton"