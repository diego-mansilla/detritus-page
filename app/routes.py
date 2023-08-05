import os
from flask import render_template, request
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import plotly
import numpy as np
from app import app

DEST_DIR = 'static/images'
IMG_SIZE = (160, 160)

def get_file_name(subdir):
    return subdir[subdir.rfind('/')+1:]

def get_class_name(path):
    parent_dir_path = os.path.dirname(path)
    parent_dir_name = os.path.basename(parent_dir_path)
    if parent_dir_name == "Detritus":
        return "Non Plankton"
    return "Plankton"

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

@app.route('/update_labels', methods=['POST'])
def update_labels():
    labels = request.json.get('labels')
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

mode_map = {
    0: "Testing",
    1: "Validation",
    2: "Training",
}

# Can be removed from px.scatter params if it is less clear'
color_discrete_map={
    "Detritus4": '#ff0000',
    "Detritus3": '#ff0000',
    "Detritus2": '#ff0000',
    "Detritus1": '#ff0000',
    "Detritus0": '#ff0000',

    "Other4": '#1629d8',
    "Other3": '#1629d8',
    "Other2": '#1629d8',
    "Other1": '#1629d8',
    "Other0": '#1629d8',
    
    "LClass_Appendic_Unfoc": '#B31A6B',
    "LClass_Dino_Cer_Tric_Mass": '#C46B19',
    "LClass_Dino_Cer_Trip_Brev": '#AFBC8A',
    "LClass_Tontonia": '#13DC72',
    "LClass_Appendic": '#5B8E6B',
    "LClass_Cnidaria": '#F14227',
    "LClass_Phy_Dia_Chain": '#705E52',
    "LClass_Cop_Calanoida_Unfoc": '#B6E697',
    "LClass_Cop_Calanoida": '#BFBC57',
    "LClass_Cop_Poec": '#B7F58A',
    "LClass_Phyto_Rhizosolenia": '#F80C73',
    "LClass_Detritus": '#A5538D',
    "LClass_Cop_Cut": '#C80EE0',
    "LClass_Nauplii_Cop": '#B54E22',
    "LClass_shadow": '#DD926D',
    "LClass_Cop_Cyclo_Unfoc": '#848290',
    "LClass_Zoothamnium_sp1": '#4160F4',
    "LClass_Asterionellopsis": '#8F31F9',
    "LClass_Phy_Dia_Pennate_Curved": '#AA7D7F',
    "LClass_Dino_Cer_Fur_Lin": '#42FA79',
    "LClass_Cop_Ecdise": '#24206D',
    "LClass_Filaments_Unfoc": '#7F6ECA',
    "LClass_Filaments": '#CD51F2',
    "LClass_Phy_Cosci_Unfoc": '#4A1E95',
    "LClass_Phy_Dia_Quadrada": '#2E06F4',
    "LClass_Cop_Cyclo": '#ADA7FD',
    "LClass_Ciliate": '#0C45BC',
    "LClass_Cladoc_Evad": '#72015D',
    "LClass_Tintin_favella": '#7F4ABB',
    "LClass_Acantharia_sp": '#F2C7E3',
    "LClass_Phy_Dia_Pennate_Fina": '#DDFE62',
    "LClass_Silicoflagellate": '#2B8640',
    "LClass_Unknown_2": '#335A18',
    "LClass_Phy_Dia_Cosci": '#FC34A6',
    "LClass_Cnidaria_Unfoc": '#DC0EFB',
    "LClass_Larvae_veliger": '#46ABDB',
    "LClass_Phy_Dia_Spiral": '#D52BDC',
    "LClass_Turbellaria": '#39D0A8',
    "LClass_Phy_Dia_Chaet": '#15080B',
    "LClass_Phy_Dia_Pennate_Gorda": '#0F7658',
    "LClass_outros": '#EB3925',
    "LClass_Phy_Dia_Hemiaulus_1_NOVA": '#A9EC7E',
    "LClass_Phy_Dia_General": '#7328DD',
    "LClass_Cladoc_Pen": '#95A89F',
    "LClass_Pelotas": '#41695F',
    "LClass_Larvae_Decapod": '#EE964B',
    "LClass_Chaetognatha": '#11CACE',
    "LClass_Dino_Noct": '#68F094',
    "LClass_Larvae_Polyc": '#D07CC6',
    "LClass_Emaranhado": '#CAB787',
    "LClass_Phy_dia_sp1": '#AABBA0',
    "LClass_diatom_bolinha": '#302F7B',
    "LClass_Cop_Harpacticoida": '#22F721',
    "LClass_Cyano_Tricho_Tuff": '#AF2093',
    "LClass_Phyt_dia_meia_lua": '#B78AF3',
    "LClass_Cladoc_Pen_Unfoc": '#68218D',
    "LClass_Dino_Cer_Tripus_I": '#4B5B64',
    "LClass_Briozoario": '#A5DD5D',
    "LClass_Ictio": '#43CA56',
    "LClass_Zoothamnium_sp2": '#B11939',
    "LClass_Phoronida": '#DE9859',
    "LClass_Larvae_Echnoderm": '#38514A',
    "LClass_Nauplii_Temora": '#9739E2',
    "LClass_Bubbles": '#8E6782',
    "LClass_Radiolaria": '#EF59F1',
    "LClass_Unknown_3": '#1E565B',
    "LClass_Amoeba": '#FE6636',
    "LClass_Nauplii_Cirripedia": '#2CD32B',
    "LClass_Rotifera": '#BE1969',
    "LClass_Bivalve": '#7A3819',
    "LClass_Sticholonche_zanclea": '#87E624',
    "LClass_Ctenophora": '#3350DA',
    "LClass_Unknown_1": '#98AD7B',
    "LClass_Cypris": '#C0F36E',
}