import pandas as pd
import os
import json
from app.utils import get_class_name, get_file_name, read_file
from app.config import inverse, reviewed_images_dict

TEST_SHEET_NUMBER = 0
VAL_SHEET_NUMBER = 1
TRAIN_SHEET_NUMBER = 2

class DenseNetFilePrediction:
    def __init__(self, name, ground_truth_label, dense_x, dense_y, nmf, pred_label, kNNList, dataset):
        self.name = name
        self.ground_truth_label = ground_truth_label
        self.densenet_position = (dense_x, dense_y)
        self.number_of_models_failed = nmf
        self.prediction_label = pred_label
        self.dataset = dataset
        self.kNNList = []
        if kNNList is not None:
            self.kNNList = kNNList
        self.expert_prediction = None 
        if name in reviewed_images_dict:
            self.expert_prediction = reviewed_images_dict[name]
    
    def to_dict(self):
        # Customize serialization for specific types
        return {
            "name": self.name,
            "ground_truth_label": self.ground_truth_label,
            "densenet_position": list(self.densenet_position),  # Convert tuple to list
            "number_of_models_failed": self.number_of_models_failed,
            "prediction_label": self.prediction_label,
            "kNNList": self.kNNList,
            "expert_prediction": self.expert_prediction,
            "dataset": self.dataset,
        }

    def to_json(self):
        # Use the customized to_dict method for JSON serialization
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def from_dict(cls, data):
        # Make sure to extract dense_x and dense_y from densenet_position or directly from data
        dense_x, dense_y = data.get('densenet_position', [None, None])
        # Now call the constructor with the extracted values and other data
        return cls(
            name=data['name'],
            ground_truth_label=data['ground_truth_label'],
            dense_x=dense_x,
            dense_y=dense_y,
            nmf=data['number_of_models_failed'],
            pred_label=data['prediction_label'],
            dataset=data['dataset'],
            kNNList=data.get('kNNList', [])  # Provide a default value if kNNList is not in data
        )

def get_files_dict(mode):
    df = pd.read_excel('detritus2.xlsx', sheet_name=int(mode))
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    df = df.iloc[: , 3:]

    pred_dict = {}
    dataset = "UNKNOWN"
    if mode == TRAIN_SHEET_NUMBER:
        dataset = "TRAINING"
    if mode == VAL_SHEET_NUMBER:
        dataset = "VALIDATION"
    if mode == TEST_SHEET_NUMBER:
        dataset = "TESTING"
        
    for i, file_name in enumerate(df['File']):
        name = get_file_name(file_name)
        ground_truth = get_class_name(file_name)

        prediction = ground_truth
        if df['DenseNet_Model_Pred'][i + 1] == "N":
            prediction = inverse[prediction]

        file_prediction = DenseNetFilePrediction(
            name=name, 
            ground_truth_label=ground_truth, 
            dense_x=df['densenet_x'][i + 1], 
            dense_y=df['densenet_y'][i + 1],
            nmf=df['Wrong classifications'][i + 1],
            pred_label=prediction,
            dataset=dataset,
            kNNList=None,
        )

        pred_dict[name] = file_prediction
    
    return pred_dict

def populate_K_list(pred_dict):
    images_input, _ = read_file('densenet.txt')

    current_image = None
    for i, img in enumerate(images_input):
        if i % 6 == 0:
            if img in pred_dict: 
                current_image = pred_dict[img]
            else:
                current_image = None
                print("Not in pred_dict img")
        elif current_image is not None:  # Ensure current_image is not None before appending
            current_image.kNNList.append(img)

def get_all_files_dict():
    test_dict = get_files_dict(TEST_SHEET_NUMBER)
    train_dict = get_files_dict(TRAIN_SHEET_NUMBER)
    val_dict = get_files_dict(VAL_SHEET_NUMBER)
    pred_dict = {**test_dict, **train_dict, **val_dict}
    populate_K_list(pred_dict)
    return pred_dict


def save_to_file(data):
    """
    Saves the data to a text file, named based on the mode.
    """
    file_path = f"files_dict.txt"
    with open(file_path, 'w') as f:
        json.dump(data, f)

def load_from_file():
    """
    Loads the data from a text file and reconstructs DenseNetFilePrediction instances.
    """
    file_path = f"files_dict.txt"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data_dict = json.load(f)
            # Reconstruct DenseNetFilePrediction instances from dictionaries
            reconstructed_dict = {key: DenseNetFilePrediction.from_dict(value) for key, value in data_dict.items()}
            return reconstructed_dict
    return None

def get_or_load_files_dict():
    """
    Attempts to load the files_dict from a file for the given mode.
    If the file doesn't exist, generates the files_dict, saves it, and returns it.
    """
    loaded_data = load_from_file()
    if loaded_data is not None:
        return loaded_data

    files_dict = get_all_files_dict()
    serializable_prediction_map = {key: value.to_dict() for key, value in files_dict.items()}
    save_to_file(serializable_prediction_map)
    return load_from_file()
