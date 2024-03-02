import os
from flask import render_template, request, jsonify
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
from scipy import spatial
import plotly
import numpy as np
from plotly.subplots import make_subplots
from app import app
from app.config import reviewed_label_map, reviewed_color_map, mode_map, formal_name_map, inverse, color_discrete_map, reviewed_images_dict
from app.utils import get_class_name, get_file_name
from app.data import get_files_dict

TEST_SHEET_NUMBER = 0
VAL_SHEET_NUMBER = 1

DEST_DIR = 'static/images'
IMG_SIZE = (160, 160)

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
def main():
    return render_template('main.html')

@app.route('/<path:model>/<path:mode>')
def home(model, mode):
    data_source = 'images/'
    if mode == "1":
        data_source = 'images_resized/'
    images_input , labels = read_file(model + '.txt')
    images = [data_source + img for img in images_input]
    return render_template('home.html', images=images, labels=labels, model=model)

@app.route('/review/<path:model>/<path:mode>')
def review(model, mode):
    data_source = 'images_resized/'
    images_input , labels = read_file(model + '.txt')
    undetermined = []
    undetermined_label = []
    pred_label = []
    search = "Indefinido"
    if mode == "1":
        search = "Plancton"
    if mode == "2":
        search = "Detritos"

    for idx, img in enumerate(images_input):
        if img in reviewed_images_dict:
            val = reviewed_images_dict[img]
            if val == search:
                print(img)
                undetermined.append(data_source + images_input[idx])
                undetermined.append(data_source + images_input[idx+1])
                undetermined.append(data_source + images_input[idx+2])
                undetermined.append(data_source + images_input[idx+3])
                undetermined.append(data_source + images_input[idx+4])
                undetermined.append(data_source + images_input[idx+5])
                
                undetermined_label.append(labels[idx])
                undetermined_label.append(labels[idx+1])
                undetermined_label.append(labels[idx+2])
                undetermined_label.append(labels[idx+3])
                undetermined_label.append(labels[idx+4])
                undetermined_label.append(labels[idx+5])

                pred_label.append(inverse[labels[idx]])
                pred_label.append(labels[idx+1])
                pred_label.append(labels[idx+2])
                pred_label.append(labels[idx+3])
                pred_label.append(labels[idx+4])
                pred_label.append(labels[idx+5])

    search = "Undetermined"
    if mode == "1":
        search = "Plankton"
    if mode == "2":
        search = "Non Plankton"

    return render_template('review.html', undetermined=undetermined, undetermined_label=undetermined_label, pred_label=pred_label, search=search, model=model)

@app.route('/update_labels', methods=['POST'])
def update_labels():
    _ = request.json.get('labels')
    url = request.json.get('url')
    print(url)
    return '', 204

@app.route('/plot/<path:mode>')
def tsnemap(mode):
    df = pd.read_excel('detritus2.xlsx', sheet_name=int(mode))
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    df = df.iloc[: , 3:]
    df['Ground Truth'] = df['Real_class_name']
    color=[df['Ground Truth'][i + 1] for i in range(len(df['Ground Truth']))]

    graphs = []
    models = ['Densenet', 'InceptionResnet', 'MobileNet', 'Simple']

    fig = px.scatter(x=df['densenet_x'], y=df['densenet_y'], color=color,  color_discrete_map=color_discrete_map, template='plotly_white')
    div = plotly.offline.plot(fig, output_type='div')
    graphs.append(div)

    fig = px.scatter(x=df['inception_resnet_x'], y=df['inception_resnet_y'], color=color,  color_discrete_map=color_discrete_map, template='plotly_white')
    div = plotly.offline.plot(fig, output_type='div')
    graphs.append(div)

    fig = px.scatter(x=df['mobilenet_x'], y=df['mobilenet_y'], color=color,  color_discrete_map=color_discrete_map, template='plotly_white')
    div = plotly.offline.plot(fig, output_type='div')
    graphs.append(div)

    fig = px.scatter(x=df['simple_model_x'], y=df['simple_model_y'], color=color,  color_discrete_map=color_discrete_map, template='plotly_white')
    div = plotly.offline.plot(fig, output_type='div')
    graphs.append(div)
    

    return render_template('plot.html', graphs=graphs, models=models, mode=mode_map[int(mode)])

def add_reviewed_to_fig(df, fig, files_dict):
    indefinido = {}
    indefinido['x'] = []
    indefinido['y'] = []

    detritos = {}
    detritos['x'] = []
    detritos['y'] = []

    plancton = {}
    plancton['x'] = []
    plancton['y'] = []

    for key, value in reviewed_images_dict.items():
        if key not in files_dict:
            continue
        file_pred = files_dict[key]
        x, y = file_pred.densenet_position
        if value == "Indefinido":
            indefinido['x'].append(x)
            indefinido['y'].append(y)

        if value == "Detritos":
            detritos['x'].append(x)
            detritos['y'].append(y)

        if value == "Plancton":
            plancton['x'].append(x)
            plancton['y'].append(y)

    fig.add_trace(
            go.Scatter(x=indefinido['x'], y=indefinido['y'], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Indefinido'],
                    size=8,
                    colorscale='Hot',
                    line=dict(
                        color='Black',
                        width=2
                    ),
                ), name=reviewed_label_map['Indefinido']),
                secondary_y=True,
            )

    fig.add_trace(
            go.Scatter(x=detritos['x'], y=detritos['y'], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Detritos'],
                    size=8,
                    colorscale='Hot',
                    line=dict(
                        color='Black',
                        width=2
                    ),
                ), name=reviewed_label_map['Detritos']),
                secondary_y=True,
            )

    fig.add_trace(
            go.Scatter(x=plancton['x'], y=plancton['y'], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Plancton'],
                    size=8,
                    colorscale='Hot',
                    line=dict(
                        color='Black',
                        width=2
                    ),
                ), name=reviewed_label_map['Plancton']),
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

    files_dict = get_files_dict(mode)

    color_prediction=[]
    dx_prediction = []
    dy_prediction = []

    for i, label in enumerate(df['Ground Truth']):
        if df['DenseNet_Model_Pred'][i+1] == 'N':
            color_prediction.append(label)
            dx_prediction.append(df['densenet_x'][i + 1])
            dy_prediction.append(df['densenet_y'][i + 1])

        coord_tuple = (df['densenet_x'][i + 1], df['densenet_y'][i + 1])
        if coord_tuple not in image_coord_dict:
            image_coord_dict[coord_tuple] = (get_file_name(df['File'][i + 1]), df['Ground Truth'][i + 1])

    graphs = []
    models = ['Densenet']

    df0, df1, df2, df3_1, df3_2, df4_1, df4_2 = get_tsne_points(df, "densenet", 5, color)
    mx = "densenet_x"
    my = "densenet_y"

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
    go.Scatter(x=df['densenet_x'].to_numpy(), y=df['densenet_y'].to_numpy(), opacity=0.1, mode='markers', marker=dict(
            color=[color_discrete_map[x] for x in color],
            size=6,
            colorscale='Hot',
        ), name="Ground Truth labels"),
        secondary_y=False,
    )

    fig.add_trace(
    go.Scatter(x=dx_prediction, y=dy_prediction, opacity=0.5, mode='markers', marker=dict(
            color=[color_discrete_map[x] for x in color_prediction],
            size=6,
            colorscale='Hot',
            line=dict(
                color='Black',
                width=1,
            )
        ), name="Ground Truth labels of Points that failed in prediction"),
        secondary_y=True,
    )

    fig.add_trace(
    go.Scatter(x=df4_1[mx], y=df4_1[my], opacity=1.0,  mode='markers', marker=dict(
            color=df4_1['color'],
            size=10,
            colorscale='Hot',
            line=dict(
                color='Black',
                width=1,
            )
        ), name="GT of points that failed classification in the 4 models"),
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

    add_reviewed_to_fig(df, fig, files_dict)

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

    image_name, image_label = image_info
    image_path = 'static/images_resized/' + image_name  # Adjust this path as necessary
    expert_label = ""
    prediction = image_label
    if image_name in reviewed_images_dict:
        expert_label = reviewed_images_dict[image_name]
        prediction = inverse[image_label]

    # Check if the file exists
    if os.path.isfile('app/'+image_path):
        return jsonify({"imagePath": '/' + image_path, "label": formal_name_map[image_label], "prediction": formal_name_map[prediction], "expert_label": expert_label,"exists": True})
    else:
        return jsonify({"message": "Image not available", "exists": False})
