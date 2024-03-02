import pandas as pd
from app.utils import get_class_name, get_file_name
from app.config import inverse

class FilePrediction:
    def __init__(self, name, ground_truth_label, dense_x, dense_y, nmf, pred_label):
        self.name = name
        self.ground_truth_label = ground_truth_label
        self.densenet_position = (dense_x, dense_y)
        self.number_of_models_failed = nmf
        self.prediction_label = pred_label

def get_files_dict(mode):
    df = pd.read_excel('detritus2.xlsx', sheet_name=int(mode))
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    df = df.iloc[: , 3:]

    pred_dict = {}

    for i, file_name in enumerate(df['File']):
        name = get_file_name(file_name)
        ground_truth = get_class_name(file_name)

        file_prediction = FilePrediction(
            name=name, 
            ground_truth_label=ground_truth, 
            dense_x=df['densenet_x'][i + 1], 
            dense_y=df['densenet_y'][i + 1],
            nmf=df['Wrong classifications'][i + 1],
            pred_label=inverse[ground_truth],
        )

        pred_dict[name] = file_prediction
    
    return pred_dict