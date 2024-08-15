import os
from flask import render_template, request, jsonify, session
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
from scipy import spatial
import plotly
import numpy as np
from plotly.subplots import make_subplots
from app import app
from app.config import reviewed_label_map, reviewed_color_map, mode_map, formal_name_map, inverse, color_discrete_map, reviewed_images_dict
from app.utils import get_file_name, read_file
from app.data import get_or_load_files_dict
import pickle
import ast

def load_dict_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return ast.literal_eval(data)

def load_file_name_class_map(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)

IMG_SIZE = (160, 160)
DATASET_NAME = ["TESTING", "VALIDATION", "TRAINING"]
file_map = load_file_name_class_map("file_name_class_map.txt")

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/<path:model>/<path:mode>')
def home(model, mode):
    data_source = 'images/'
    if mode == "1":
        data_source = 'images_resized/'
    images_input , labels = read_file(model + '.txt')
    real_class_labels = [file_map[img] for img in images_input]
    images = [data_source + img for img in images_input]
    return render_template('home.html', images=images, labels=labels, real_labels=real_class_labels, model=model)

@app.route('/<path:clase>/incorrect')
def wrongImages(clase):
    data_map = load_dict_from_file('incorrect_files_output.txt')
    list_images = []
    if clase in data_map:
        list_images = data_map[clase]
    return render_template('wrong_images.html', images=list_images, clase=clase)

@app.route('/<path:clase>/correct')
def correctImages(clase):
    data_map = load_dict_from_file('correct_files_output.txt')
    list_images = []
    if clase in data_map:
        list_images = data_map[clase]
    return render_template('correct_images.html', images=list_images, clase=clase)

@app.route('/review/<path:model>/<path:mode>')
def review(model, mode):
    data_source = 'images_resized/'

    files_dict = get_or_load_files_dict()
    
    images = [[], [], []]
    ground_truth = [[], [], []]
    pred_label = [[], [], []]

    search = "Plankton"
    if mode == "1":
        search = "Non Plankton"

    for img, val in reviewed_images_dict.items():
        densenet_prediction = files_dict[img]
        arr_idx = 2
        if val == "Detritos":
            arr_idx = 1
        if val == "Plancton":
            arr_idx = 0

        if densenet_prediction.prediction_label == search:
            if len(densenet_prediction.kNNList) == 0:
                # TRAINING case (no images)
                print(densenet_prediction.to_dict()) 
                continue
            images[arr_idx].append(data_source + img)
            ground_truth[arr_idx].append(densenet_prediction.ground_truth_label)
            pred_label[arr_idx].append(densenet_prediction.prediction_label)
            for k in densenet_prediction.kNNList:
                k_pred = files_dict[k]
                images[arr_idx].append(data_source + k)
                ground_truth[arr_idx].append(k_pred.ground_truth_label)
                pred_label[arr_idx].append(k_pred.prediction_label)

    prepared_data = []
    for category_data, labels, predictions in zip(images, ground_truth, pred_label):
        prepared_category_data = [{
            'image': image,
            'label': label,
            'prediction': prediction
        } for image, label, prediction in zip(category_data, labels, predictions)]
        prepared_data.append(prepared_category_data)

    
    return render_template('review.html', prepared_data=prepared_data, expert_classification=["Plankton", "Non Plankton", "Undetermined"], search=search)

@app.route('/update_labels', methods=['POST'])
def update_labels():
    _ = request.json.get('labels')
    url = request.json.get('url')
    print(url)
    return '', 204

@app.route('/plot/<path:mode>')
def tsnemap(mode):
    df = pd.read_excel('detritus2.xlsx', sheet_name=int(mode))
    new_header = df.iloc[0]  # grab the first row for the header
    df = df[1:]  # take the data less the header row
    df.columns = new_header  # set the header row as the df header
    df = df.iloc[:, 3:]
    df['Ground Truth'] = df['Real_class_name']
    color = [df['Ground Truth'][i + 1] for i in range(len(df['Ground Truth']))]

    graphs = []
    models = ['Densenet', 'InceptionResnet', 'MobileNet', 'Simple']

    # For each model, generate the plot and adjust the layout
    for model_x, model_y in [('densenet_x', 'densenet_y'),
                             ('inception_resnet_x', 'inception_resnet_y'),
                             ('mobilenet_x', 'mobilenet_y'),
                             ('simple_model_x', 'simple_model_y')]:

        fig = px.scatter(x=df[model_x], y=df[model_y], color=color,
                         color_discrete_map=color_discrete_map, template='plotly_white')

        # Update layout for equal aspect ratio and larger size
        fig.update_layout(
            xaxis=dict(scaleanchor="y", scaleratio=1),
            yaxis=dict(scaleanchor="x", scaleratio=1),
            width=1500,  # Set width larger
            height=1500  # Set height larger
        )

        div = plotly.offline.plot(fig, output_type='div')
        graphs.append(div)

    return render_template('plot.html', graphs=graphs, models=models, mode=mode_map[int(mode)])


def add_reviewed_to_fig(fig, files_dict, mode):
    indefinido = {}
    indefinido['x'] = []
    indefinido['y'] = []

    detritos = {}
    detritos['x'] = [[],[]]
    detritos['y'] = [[],[]]

    plancton = {}
    plancton['x'] = [[],[]]
    plancton['y'] = [[],[]]

    for key, value in reviewed_images_dict.items():
        if key not in files_dict:
            continue
        file_pred = files_dict[key]
        if file_pred.dataset != DATASET_NAME[mode]:
            continue
        x, y = file_pred.densenet_position
        
        if file_pred.prediction_label == formal_name_map[value]:
            if value == "Detritos":
                detritos['x'][0].append(x)
                detritos['y'][0].append(y)

            if value == "Plancton":
                plancton['x'][0].append(x)
                plancton['y'][0].append(y)

        else:
            if value == "Detritos":
                detritos['x'][1].append(x)
                detritos['y'][1].append(y)

            if value == "Plancton":
                plancton['x'][1].append(x)
                plancton['y'][1].append(y)

            if value == "Indefinido":
                indefinido['x'].append(x)
                indefinido['y'].append(y)

        

    fig.add_trace(
            go.Scatter(x=indefinido['x'], y=indefinido['y'], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Indefinido'],
                    size=8,
                    colorscale='Hot',
                    line=dict(
                        color='Black',
                        width=2
                    ),
                ), name="Prediction mismatch with Expert: Undetermined"),
                secondary_y=True,
            )

    fig.add_trace(
            go.Scatter(x=detritos['x'][1], y=detritos['y'][1], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Detritos_Mismatch'],
                    size=8,
                    colorscale='Hot',
                    line=dict(
                        color='Black',
                        width=2
                    ),
                ), name="Prediction mismatch with Expert: Non Plankton, Prediction: Plankton"),
                secondary_y=True,
            )

    fig.add_trace(
            go.Scatter(x=plancton['x'][1], y=plancton['y'][1], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Plancton_Mismatch'],
                    size=8,
                    colorscale='Hot',
                    line=dict(
                        color='Black',
                        width=2
                    ),
                ), name="Prediction mismatch with Expert: Plankton, Prediction: Non Plankton"),
                secondary_y=True,
            )
    
    fig.add_trace(
            go.Scatter(x=detritos['x'][0], y=detritos['y'][0], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Detritos_Match'],
                    size=8,
                    colorscale='Hot',
                    line=dict(
                        color='Black',
                        width=2
                    ),
                ), name="Prediction match with Expert: Non Plankton, Prediction: Non Plankton"),
                secondary_y=True,
            )

    fig.add_trace(
            go.Scatter(x=plancton['x'][0], y=plancton['y'][0], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Plancton_Match'],
                    size=8,
                    colorscale='Hot',
                    line=dict(
                        color='Black',
                        width=2
                    ),
                ), name="Prediction match with Expert: Plankton, Prediction: Plankton"),
                secondary_y=True,
            )


def get_points(df, model, num):
    points = []
    points_map = {}
    mx = "{}_x".format(model)
    my = "{}_y".format(model)
    idx = 0
    for i, wc in enumerate(df['Wrong classifications']):
        if wc != num:
            p = (df[mx][i+1], df[my][i+1])
            points.append(p)
            assert (p not in points_map)
            points_map[idx] = i
            idx = idx + 1
    return points, points_map

def get_bad_points(df, model, K, num):
    points, points_map = get_points(df, model, num)
    kd = spatial.KDTree(points)
    indices_result = []
    not_so_bad = []
    neighbors_map = {}
    for i, wc in enumerate(df['Wrong classifications']):
        if wc == num:
            bad_point_gt = df['Ground Truth'][i + 1]
            mx = "{}_x".format(model)
            my = "{}_y".format(model)
            p = (df[mx][i+1], df[my][i+1])
            _, indices = kd.query(p, K)
            mismatch_gt = 0
            neighbors = []
            for ki in indices:
                real_ki = points_map[ki]
                neighbors.append(real_ki)
                k_point_gt = df['Ground Truth'][real_ki + 1]
                if k_point_gt != bad_point_gt:
                    mismatch_gt = mismatch_gt + 1
            if mismatch_gt == K:
                indices_result.append(i)
                neighbors_map[i] = neighbors
            else:
                not_so_bad.append(i)
    assert (len(points) + len(indices_result) + len(not_so_bad) == len(df['Wrong classifications']))
    return indices_result, not_so_bad, neighbors_map

def get_tsne_points(df, model, K, color):
    bad_points, not_bad_points, neighbors_bad_points = get_bad_points(df, model, K, 4)
    bad_points_3, not_bad_points_3, neighbors_bad_points_3 = get_bad_points(df, model, K, 3)
    mx = "{}_x".format(model)
    my = "{}_y".format(model)
    df0 = {
        mx: [],
        my: [],
        'color': [],
    }

    df1 = {
        mx: [],
        my: [],
        'color': [],
    }

    df2 = {
        mx: [],
        my: [],
        'color': [],
    }

    for i, wc in enumerate(df['Wrong classifications']):
        if wc == 0:
            df0[mx].append(df[mx][i + 1])
            df0[my].append(df[my][i + 1])
            df0['color'].append(color_discrete_map[color[i]])
        if wc == 1:
            df1[mx].append(df[mx][i + 1])
            df1[my].append(df[my][i + 1])
            df1['color'].append(color_discrete_map[color[i]])
        if wc == 2:
            df2[mx].append(df[mx][i + 1])
            df2[my].append(df[my][i + 1])
            df2['color'].append(color_discrete_map[color[i]])

    df3_1={
        mx:  [df[mx][i + 1] for _, i in enumerate(not_bad_points_3)],
        my:[df[my][i + 1] for _, i in enumerate(not_bad_points_3)],
        'color': [color_discrete_map[color[i]] for _, i in enumerate(not_bad_points_3)],
    }

    df3_2={
        mx:  [df[mx][i + 1] for _, i in enumerate(bad_points_3)],
        my:[df[my][i + 1] for _, i in enumerate(bad_points_3)],
        'color': [color_discrete_map[color[i]] for _, i in enumerate(bad_points_3)],
    }

    df4_1={
        mx:  [df[mx][i + 1] for _, i in enumerate(not_bad_points)],
        my:[df[my][i + 1] for _, i in enumerate(not_bad_points)],
        'color': [color_discrete_map[color[i]] for _, i in enumerate(not_bad_points)],
    }

    df4_2={
        mx:  [df[mx][i + 1] for _, i in enumerate(bad_points)],
        my:[df[my][i + 1] for _, i in enumerate(bad_points)],
        'color': [color_discrete_map[color[i]] for _, i in enumerate(bad_points)],
    }
    
    return df0, df1, df2, df3_1, df3_2, df4_1, df4_2

image_coord_dict = {}

@app.route('/plot_densenet/<path:mode>')
def tsnemap_densenet(mode):
    df = pd.read_excel('detritus2.xlsx', sheet_name=int(mode))
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    df = df.iloc[: , 3:]

    #define list of columns range
    cols = [x for x in range(df.shape[1])]


    df = df.iloc[:, cols]

    color=[df['Ground Truth'][i + 1] for i in range(len(df['Ground Truth']))]

    files_dict = get_or_load_files_dict()

    for i, _ in enumerate(df['Ground Truth']):
        coord_tuple = (df['densenet_x'][i + 1], df['densenet_y'][i + 1])
        if coord_tuple not in image_coord_dict:
            image_coord_dict[coord_tuple] = (get_file_name(df['File'][i + 1]), df['Ground Truth'][i + 1])

    graphs = []
    models = ['Densenet']

    df0, df1, df2, df3_1, df3_2, df4_1, df4_2 = get_tsne_points(df, "densenet", 5, color)
    mx = "densenet_x"
    my = "densenet_y"

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    plankton_filtered_array = [
        item for item in files_dict.values() 
        if item.dataset == DATASET_NAME[int(mode)] and item.ground_truth_label == "Plankton"
    ]

    detritus_filtered_array = [
        item for item in files_dict.values() 
        if item.dataset == DATASET_NAME[int(mode)] and item.ground_truth_label == "Non Plankton"
    ]

    fig.add_trace(
    go.Scatter(x=[obj.densenet_position[0] for obj in plankton_filtered_array], y=[obj.densenet_position[1] for obj in plankton_filtered_array], opacity=0.1, mode='markers', marker=dict(
            color=[color_discrete_map[x] for x in [obj.ground_truth_label for obj in plankton_filtered_array]],
            size=6,
            colorscale='Hot',
        ), name="Ground Truth labels Plankton"),
        secondary_y=False,
    )

    fig.add_trace(
    go.Scatter(x=[obj.densenet_position[0] for obj in detritus_filtered_array], y=[obj.densenet_position[1] for obj in detritus_filtered_array], opacity=0.1, mode='markers', marker=dict(
            color=[color_discrete_map[x] for x in [obj.ground_truth_label for obj in detritus_filtered_array]],
            size=6,
            colorscale='Hot',
        ), name="Ground Truth labels Non Plankton"),
        secondary_y=False,
    )

    detritus_filtered_array = [
        item for item in files_dict.values() 
        if item.dataset == DATASET_NAME[int(mode)] and item.ground_truth_label == "Non Plankton"
        and item.prediction_label != item.ground_truth_label
    ]

    plankton_filtered_array = [
        item for item in files_dict.values() 
        if item.dataset == DATASET_NAME[int(mode)] and item.ground_truth_label == "Plankton"
        and item.prediction_label != item.ground_truth_label
    ]

    fig.add_trace(
    go.Scatter(x=[obj.densenet_position[0] for obj in detritus_filtered_array], y=[obj.densenet_position[1] for obj in detritus_filtered_array], opacity=0.5, mode='markers', marker=dict(
            color=[color_discrete_map[x] for x in [obj.ground_truth_label for obj in detritus_filtered_array]],
            size=6,
            colorscale='Hot',
            line=dict(
                color='Black',
                width=1,
            )
        ), name="GT Label: Non Plankton, Prediction: Plakton DenseNet Mismatch"),
        secondary_y=True,
    )

    fig.add_trace(
    go.Scatter(x=[obj.densenet_position[0] for obj in plankton_filtered_array], y=[obj.densenet_position[1] for obj in plankton_filtered_array], opacity=0.5, mode='markers', marker=dict(
            color=[color_discrete_map[x] for x in [obj.ground_truth_label for obj in plankton_filtered_array]],
            size=6,
            colorscale='Hot',
            line=dict(
                color='Black',
                width=1,
            )
        ), name="GT Label: Plankton, Prediction: Non Plankton DenseNet Mismatch"),
        secondary_y=True,
    )

    detritus_filtered_array = [
        item for item in files_dict.values() 
        if item.dataset == DATASET_NAME[int(mode)] and item.ground_truth_label == "Non Plankton"
        and item.number_of_models_failed == 4
    ]

    plankton_filtered_array = [
        item for item in files_dict.values() 
        if item.dataset == DATASET_NAME[int(mode)] and item.ground_truth_label == "Plankton"
        and item.number_of_models_failed == 4
    ]

    fig.add_trace(
    go.Scatter(x=[obj.densenet_position[0] for obj in plankton_filtered_array], y=[obj.densenet_position[1] for obj in plankton_filtered_array], opacity=1.0, mode='markers', marker=dict(
            color=[color_discrete_map[x] for x in [obj.ground_truth_label for obj in plankton_filtered_array]],
            size=10,
            colorscale='Hot',
            line=dict(
                color='Black',
                width=1,
            )
        ), name="GT Label: Plankton, Prediction: Non Plankton 4 Models Mismatch"),
        secondary_y=True,
    )
    
    fig.add_trace(
    go.Scatter(x=[obj.densenet_position[0] for obj in detritus_filtered_array], y=[obj.densenet_position[1] for obj in detritus_filtered_array], opacity=1.0, mode='markers', marker=dict(
            color=[color_discrete_map[x] for x in [obj.ground_truth_label for obj in detritus_filtered_array]],
            size=10,
            colorscale='Hot',
            line=dict(
                color='Black',
                width=1,
            )
        ), name="GT Label: Non Plankton, Prediction: Plankton 4 Models Mismatch"),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(x=df4_2[mx], y=df4_2[my], opacity=1.0,  mode='markers', marker=dict(
                color=df4_2['color'],
                size=10,
                colorscale='Hot',
                line=dict(
                    color='Black',
                    width=2
                )
            ), name="GT of points that failed classification in the 4 models and have K nearest neighbors of different GT"),
        secondary_y=True,
    )

    add_reviewed_to_fig(fig, files_dict, int(mode))

    # Set the layout to be responsive in width and adjust the height accordingly
    fig.update_layout(
        autosize=True,
        width=None,  # Width will be automatically adjusted
        height=800,  # Height will be automatically adjusted
        margin=dict(l=20, r=20, t=20, b=20),  # Adjust margins to your needs
    )

    div = plotly.offline.plot(fig, output_type='div')
    graphs.append(div)
    
    return render_template('plot.html', graphs=graphs, models=models, mode=mode_map[int(mode)])

@app.route('/get_image', methods=['POST'])
def get_image():
    data = request.json
    x = data['x']
    y = data['y']
    # Assuming image_coord_dict maps coordinates to a tuple of (image_name, label)
    image_info = image_coord_dict.get((x, y), ("not_exist", "No label"))
    
    files_dict = get_or_load_files_dict()

    image_name, _ = image_info
    image_path = 'static/images_resized/' + image_name  # Adjust this path as necessary

    densenet_file_prediction = files_dict[image_name]
    
    knn_image_paths = [
        '/static/images_resized/' + knn_image_name for knn_image_name in densenet_file_prediction.kNNList
    ]

    knn_image_label = [
        file_map[knn_image_name] for knn_image_name in densenet_file_prediction.kNNList
    ]

    print(densenet_file_prediction.to_dict())

    # Check if the file exists
    if os.path.isfile('app/'+image_path):
        return jsonify({
            "imagePath": '/' + image_path, 
            "label": densenet_file_prediction.ground_truth_label,
            "real_label": file_map[image_name],
            "prediction": densenet_file_prediction.prediction_label,
            "expert_label": densenet_file_prediction.expert_prediction,
            "knnImagePaths": knn_image_paths,
            "knnImageLabel": knn_image_label,
            "failed_models": densenet_file_prediction.number_of_models_failed,
            "name": image_name,
            "exists": True,
        })
    else:
        return jsonify({
            "message": "Image not available", 
            "name": image_name,
            "label": densenet_file_prediction.ground_truth_label,
            "real_label": file_map[image_name],
            "prediction": densenet_file_prediction.prediction_label,
            "expert_label": densenet_file_prediction.expert_prediction,
            "failed_models": densenet_file_prediction.number_of_models_failed,
            "exists": False
        })
