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

reviewed_color_map={
    "Indefinido": '#FFBF00',
    "Detritos": '#5a3880',
    "Plancton": '#6ffffb',
}

reviewed_label_map={
    "Indefinido": 'Undetermined',
    "Detritos": 'Non-Plankton',
    "Plancton": 'Plankton',
}

prediction_color_discrete_map={
    "Detritus": '#ff5a1d',

    "Other": '#1dc2ff',
}

inverse={
    "Detritus": 'Other',

    "Other": 'Detritus',

    "Plankton": 'Non Plankton',

    "Non Plankton": 'Plankton',
}

# Can be removed from px.scatter params if it is less clear'
color_discrete_map={
    "Detritus4": '#ff0000',
    "Detritus3": '#ff0000',
    "Detritus2": '#ff0000',
    "Detritus1": '#ff0000',
    "Detritus0": '#ff0000',

    "Detritus": '#ff0000',

    "Other": '#1629d8',

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

reviewed_images_dict = {'frame_401_2017-09-17_09_55_34.504_1148_68.png': 'Indefinido',
 'frame_236_2017-09-17_12_02_24.860_1870_370.png': 'Indefinido',
 'frame_5_2017-09-16_01_09_39.011_1417_898.png': 'Indefinido',
 'frame_783_2017-09-16_00_06_14.278_1814_1617.png': 'Indefinido',
 'frame_78_2017-09-16_02_13_04.215_VIDEOALE_1218_1154.png': 'Indefinido',
 'frame_497_2017-09-20_18_56_48.413_975_603.png': 'Indefinido',
 'frame_599_2017-09-21_13_29_38.934_881_338.png': 'Indefinido',
 'frame_230_2017-09-18_10_56_27.071_117_859.png': 'Indefinido',
 'frame_805_2017-09-21_18_18_59.744_1651_1914.png': 'Indefinido',
 'frame_631_2017-09-28_12_09_24.725_334_1741.png': 'Indefinido',
 'frame_958_2017-09-20_18_01_09.974_432_1220.png': 'Indefinido',
 'frame_291_2017-09-19_03_08_50.128_563_1788.png': 'Indefinido',
 'frame_169_2017-09-19_05_36_48.737_1738_740.png': 'Indefinido',
 'frame_126_2017-09-19_05_57_56.992_0_1650.png': 'Indefinido',
 'frame_457_2017-09-21_06_15_38.060_480_1244.png': 'Indefinido',
 'frame_633_2017-09-29_00_01_37.713_347_1180.png': 'Indefinido',
 'frame_6_2017-09-19_17_56_42.408_1357_406.png': 'Indefinido',
 'frame_38_2017-09-30_12_00_31.607_432_1023.png': 'Indefinido',
 'frame_230_2017-09-28_18_05_31.581_1233_147.png': 'Indefinido',
 'frame_241_2017-09-19_14_04_10.121_574_1603.png': 'Indefinido',
 'frame_241_2017-09-21_07_33_31.746_273_1211.png': 'Indefinido',
 'frame_191_2017-09-16_11_01_32.735_1793_840.png': 'Indefinido',
 'frame_811_2017-09-20_17_38_54.681_963_584.png': 'Indefinido',
 'frame_25_2017-09-19_12_39_36.606_575_1437.png': 'Indefinido',
 'frame_58_2017-09-19_01_02_00.347_1381_1227.png': 'Indefinido',
 'frame_68_2017-09-18_16_55_49.058_1115_828.png': 'Indefinido',
 'frame_173_2017-09-21_02_55_19.170_392_835.png': 'Indefinido',
 'frame_965_2017-09-20_18_01_09.974_167_1852.png': 'Indefinido',
 'frame_786_2017-09-22_03_57_39.662_610_1691.png': 'Indefinido',
 'frame_66_2017-09-19_05_57_56.992_439_1398.png': 'Indefinido',
 'frame_821_2017-09-16_00_06_14.278_1020_879.png': 'Indefinido',
 'frame_468_2017-09-16_01_09_39.011_894_1438.png': 'Indefinido',
 'frame_162_2017-09-21_02_55_19.170_1421_1298.png': 'Indefinido',
 'frame_532_2017-09-21_13_29_38.934_1871_884.png': 'Indefinido',
 'frame_816_2017-09-21_18_07_51.879_950_997.png': 'Indefinido',
 'frame_770_2017-09-21_04_46_36.462_625_740.png': 'Indefinido',
 'frame_73_2017-09-20_19_41_19.269_1308_1181.png': 'Indefinido',
 'frame_909_2017-09-20_16_21_00.715_749_1838.png': 'Indefinido',
 'frame_233_2017-09-19_20_24_40.789_892_266.png': 'Indefinido',
 'frame_636_2017-09-29_12_04_58.884_966_1568.png': 'Indefinido',
 'frame_103_2017-09-19_06_19_05.639_1833_155.png': 'Indefinido',
 'frame_86_2017-09-18_06_00_30.097_0_562.png': 'Indefinido',
 'frame_636_2017-09-21_18_07_51.879_607_1916.png': 'Indefinido',
 'frame_962_2017-09-20_18_23_25.361_242_289.png': 'Indefinido',
 'frame_969_2017-09-20_18_01_09.974_1444_1019.png': 'Indefinido',
 'frame_327_2017-09-19_11_15_03.115_543_622.png': 'Indefinido',
 'frame_159_2017-09-21_02_55_19.170_1586_1511.png': 'Indefinido',
 'frame_942_2017-09-20_23_57_16.170_258_406.png': 'Indefinido',
 'frame_180_2017-09-16_14_11_48.478_1327_50.png': 'Indefinido',
 'frame_813_2017-09-20_17_38_54.681_1792_986.png': 'Indefinido',
 'frame_170_2017-09-18_13_03_16.745_1586_1558.png': 'Indefinido',
 'frame_632_2017-09-22_03_57_39.662_939_1410.png': 'Indefinido',
 'frame_967_2017-09-20_18_01_09.974_756_1365.png': 'Indefinido',
 'frame_248_2017-09-18_14_06_42.125_1671_1475.png': 'Indefinido',
 'frame_361_2017-09-18_13_03_16.745_543_1941.png': 'Indefinido',
 'frame_509_2017-09-16_01_09_39.011_1094_676.png': 'Indefinido',
 'frame_906_2017-09-22_18_03_26.967_320_698.png': 'Indefinido',
 'frame_633_2017-09-22_03_57_39.662_221_671.png': 'Plancton',
 'frame_508_2017-09-27_05_55_28.248_1163_1260.png': 'Plancton',
 'frame_905_2017-09-23_12_02_54.587_1752_1582.png': 'Plancton',
 'frame_821_2017-09-20_23_57_16.170_4_222.png': 'Plancton',
 'frame_349_2017-09-20_20_59_12.793_404_185.png': 'Plancton',
 'frame_695_2017-09-20_18_56_48.413_944_904.png': 'Plancton',
 'frame_638_2017-09-23_12_02_54.587_558_1780.png': 'Plancton',
 'frame_507_2017-09-27_05_55_28.248_419_1557.png': 'Plancton',
 'frame_425_2017-09-18_16_55_49.058_1469_1771.png': 'Plancton',
 'frame_620_2017-09-21_22_57_12.103_437_0.png': 'Plancton',
 'frame_565_2017-09-18_13_03_16.745_1721_888.png': 'Plancton',
 'frame_387_2017-09-23_12_02_54.587_1788_43.png': 'Plancton',
 'frame_272_2017-09-22_11_56_11.306_1361_1781.png': 'Plancton',
 'frame_214_2017-09-21_22_57_12.103_283_1069.png': 'Plancton',
 'frame_826_2017-09-21_12_45_07.826_1215_1873.png': 'Plancton',
 'frame_857_2017-09-21_20_21_24.131_907_759.png': 'Plancton',
 'frame_431_2017-09-20_23_01_37.642_787_228.png': 'Plancton',
 '2017-09-19_21_29_51_1301_390.png': 'Plancton',
 'frame_757_2017-09-20_23_46_08.531_1683_768.png': 'Plancton',
 'frame_590_2017-09-16_05_02_10.850_542_414.png': 'Plancton',
 'frame_5_2017-09-21_04_13_13.353_1984_1178.png': 'Plancton',
 'frame_358_2017-09-19_13_21_55.011_205_1123.png': 'Plancton',
 'frame_4_2017-09-21_04_13_13.353_1428_185.png': 'Plancton',
 'frame_776_2017-09-22_03_57_39.662_1182_1887.png': 'Plancton',
 'frame_447_2017-09-19_04_33_23.799_949_282.png': 'Plancton',
 'frame_43_2017-09-19_11_15_03.115_779_76.png': 'Plancton',
 'frame_614_2017-09-23_06_06_47.168_1360_1907.png': 'Plancton',
 'frame_651_2017-09-22_03_57_39.662_9_285.png': 'Plancton',
 'frame_322_2017-09-23_00_10_41.055_1238_206.png': 'Plancton',
 'frame_317_2017-09-21_07_33_31.746_1771_363.png': 'Plancton',
 'frame_65_2017-09-20_16_21_00.715_1227_601.png': 'Plancton',
 'frame_348_2017-09-19_13_21_55.011_1093_456.png': 'Plancton',
 'frame_798_2017-09-20_23_46_08.531_550_1716.png': 'Plancton',
 'frame_415_2017-09-18_13_03_16.745_1598_253.png': 'Plancton',
 'frame_552_2017-09-21_18_18_59.744_1716_893.png': 'Plancton',
 'frame_791_2017-09-30_12_00_31.607_1211_1040.png': 'Plancton',
 'frame_19_2017-09-18_00_01_08.787_1318_1946.png': 'Plancton',
 'frame_827_2017-09-20_15_36_29.632_991_1782.png': 'Plancton',
 'frame_270_2017-09-22_11_56_11.306_1437_1582.png': 'Plancton',
 'frame_804_2017-09-22_03_57_39.662_1722_151.png': 'Plancton',
 'frame_632_2017-09-21_02_55_19.170_792_686.png': 'Plancton',
 'frame_174_2017-09-20_17_38_54.681_1744_1304.png': 'Plancton',
 'frame_333_2017-09-17_21_54_18.614_154_1112.png': 'Detritos',
 'frame_686_2017-09-27_00_10_30.061_388_367.png': 'Detritos',
 'frame_966_2017-09-20_18_01_09.974_440_1609.png': 'Detritos',
 'frame_195_2017-09-18_09_10_45.236_1625_16.png': 'Detritos',
 'frame_794_2017-09-22_03_57_39.662_0_749.png': 'Detritos',
 'frame_584_2017-09-21_01_26_17.933_1772_1438.png': 'Detritos',
 'frame_127_2017-09-30_12_00_31.607_220_345.png': 'Detritos',
 'frame_810_2017-09-21_19_36_53.362_827_58.png': 'Detritos',
 'frame_428_2017-09-17_21_54_18.614_1505_624.png': 'Detritos',
 'frame_288_2017-09-19_08_25_56.024_874_327.png': 'Detritos',
 'frame_280_2017-09-20_20_59_12.793_1331_703.png': 'Detritos',
 'frame_616_2017-09-21_20_54_47.206_328_191.png': 'Detritos',
 'frame_266_2017-09-21_19_03_30.206_0_512.png': 'Detritos',
 'frame_970_2017-09-20_18_01_09.974_1920_1145.png': 'Detritos',
 'frame_258_2017-09-20_18_01_09.974_526_23.png': 'Detritos',
 'frame_622_2017-09-16_06_05_35.531_1332_1191.png': 'Detritos',
 'frame_452_2017-09-16_03_58_45.702_1843_733.png': 'Detritos',
 'frame_340_2017-09-18_09_10_45.236_418_203.png': 'Detritos',
 'frame_489_2017-09-20_20_25_49.768_1443_1309.png': 'Detritos',
 'frame_103_2017-09-19_00_19_43.344_1250_603.png': 'Detritos',
 'frame_16_2017-09-17_21_54_18.614_175_493.png': 'Detritos',
 'frame_235_2017-09-20_23_46_08.531_1943_1797.png': 'Detritos',
 'frame_137_2017-09-21_20_54_47.206_1138_1020.png': 'Detritos',
 'frame_325_2017-09-17_00_03_41.880_1888_1931.png': 'Detritos',
 'frame_315_2017-09-18_13_03_16.745_1607_871.png': 'Detritos',
 'frame_749_2017-09-21_18_07_51.879_1819_453.png': 'Detritos',
 'frame_113_2017-10-06_20_57_23.135_645_484.png': 'Detritos',
 'frame_552_2017-09-21_02_10_48.705_227_1067.png': 'Detritos',
 'frame_222_2017-09-18_08_07_19.921_533_1482.png': 'Detritos',
 'frame_522_2017-09-19_05_15_40.665_850_395.png': 'Detritos',
 'frame_755_2017-09-20_15_36_29.632_1601_86.png': 'Detritos',
 'frame_369_2017-09-16_01_09_39.011_1930_737.png': 'Detritos',
 'frame_931_2017-09-21_00_08_23.959_850_1437.png': 'Detritos',
 'frame_45_2017-09-21_18_18_59.744_850_1026.png': 'Detritos',
 'frame_88_2017-09-21_06_04_30.013_1974_747.png': 'Detritos',
 'frame_507_2017-09-16_01_09_39.011_792_808.png': 'Detritos',
 'frame_686_2017-09-27_00_10_30.061_827_127.png': 'Detritos',
 'frame_273_2017-09-28_18_05_31.581_586_644.png': 'Detritos',
 'frame_917_2017-09-20_15_36_29.632_1407_0.png': 'Detritos',
 'frame_463_2017-09-17_10_58_58.968_579_755.png': 'Detritos',
 'frame_366_2017-09-17_04_59_37.593_633_1798.png': 'Detritos',
 'frame_136_2017-09-24_06_02_23.018_1194_1392.png': 'Detritos',
 'frame_199_2017-09-17_03_56_12.949_1243_1422.png': 'Detritos',
 'frame_836_2017-09-20_18_23_25.361_124_1091.png': 'Detritos',
 'frame_322_2017-09-17_01_07_06.185_653_996.png': 'Detritos',
 'frame_254_2017-09-21_20_54_47.206_498_848.png': 'Detritos',
 'frame_449_2017-09-16_01_09_39.011_336_982.png': 'Detritos',
 'frame_485_2017-09-19_16_11_00.910_485_610.png': 'Detritos',
 'frame_667_2017-09-21_20_21_24.131_854_215.png': 'Detritos',
 'frame_202_2017-09-19_11_15_03.115_1284_1056.png': 'Detritos',
 'frame_374_2017-09-21_10_53_50.448_1417_506.png': 'Detritos',
 'frame_411_2017-09-20_23_01_37.642_492_1741.png': 'Detritos',
 'frame_374_2017-09-27_12_02_43.349_1755_1184.png': 'Detritos',
 'frame_339_2017-09-16_01_09_39.011_1476_125.png': 'Detritos',
 'frame_914_2017-09-21_00_08_23.959_768_108.png': 'Detritos',
 'frame_90_2017-09-20_20_59_12.793_1271_1960.png': 'Detritos',
 'frame_173_2017-09-20_23_46_08.531_1369_395.png': 'Detritos',
 'frame_786_2017-09-29_18_01_05.556_1546_1331.png': 'Detritos',
 'frame_697_2017-09-21_23_41_42.650_1610_681.png': 'Detritos',
 'frame_237_2017-09-21_04_46_36.462_51_1741.png': 'Detritos',
 'frame_30_2017-09-18_03_53_40.556_479_1835.png': 'Detritos',
 'frame_698_2017-09-21_23_41_42.650_994_255.png': 'Detritos',
 'frame_845_2017-09-21_09_35_56.784_1499_153.png': 'Detritos',
 'frame_802_2017-09-20_15_36_29.632_1929_1332.png': 'Detritos',
 'frame_444_2017-09-20_18_01_09.974_1428_1624.png': 'Detritos',
 'frame_602_2017-09-21_18_18_59.744_805_445.png': 'Detritos',
 'frame_955_2017-09-21_02_55_19.170_883_1461.png': 'Detritos',
 'frame_189_2017-09-21_06_49_00.820_1731_1181.png': 'Detritos',
 'frame_249_2017-09-21_11_27_13.664_1919_1942.png': 'Detritos',
 'frame_229_2017-09-19_10_32_46.066_1383_693.png': 'Detritos',
 'frame_272_2017-09-28_18_05_31.581_1504_1185.png': 'Detritos',
 'frame_781_2017-09-27_12_02_43.349_1986_746.png': 'Detritos',
 'frame_299_2017-09-21_20_54_47.206_710_1161.png': 'Detritos',
 'frame_893_2017-09-22_03_57_39.662_1904_1252.png': 'Detritos',
 'frame_18_2017-09-20_23_01_37.642_1988_932.png': 'Detritos',
 'frame_542_2017-09-21_13_29_38.934_933_1113.png': 'Detritos',
 'frame_139_2017-09-19_09_50_29.580_20_1126.png': 'Detritos',
 'frame_157_2017-09-16_11_01_32.735_17_1614.png': 'Detritos',
 'frame_85_2017-09-18_13_03_16.745_1422_1114.png': 'Detritos',
 'frame_371_2017-09-16_20_53_26.537_1036_464.png': 'Detritos',
 'frame_186_2017-09-16_02_13_04.215_VIDEOALE_1252_140.png': 'Detritos',
 'frame_145_2017-09-24_00_06_17.008_552_314.png': 'Detritos',
 'frame_783_2017-09-16_00_06_14.278_490_1322.png': 'Detritos',
 'frame_667_2017-09-21_08_06_54.700_1673_855.png': 'Detritos',
 'frame_191_2017-09-16_11_01_32.735_1810_799.png': 'Detritos',
 'frame_857_2017-09-21_10_09_19.640_1756_1843.png': 'Detritos',
 'frame_304_2017-09-18_16_55_49.058_1478_1067.png': 'Detritos',
 'frame_562_2017-10-06_20_57_23.135_1240_0.png': 'Detritos',
 'frame_723_2017-09-16_02_13_04.215_VIDEOALE_1419_637.png': 'Detritos',
 'frame_911_2017-09-21_00_08_23.959_15_575.png': 'Detritos',
 'frame_436_2017-09-20_18_56_48.413_1475_1644.png': 'Detritos',
 'frame_82_2017-09-16_01_09_39.011_817_1482.png': 'Detritos',
 'frame_136_2017-09-20_16_21_00.715_970_806.png': 'Detritos',
 'frame_765_2017-09-21_10_09_19.640_223_201.png': 'Detritos',
 'frame_760_2017-09-21_14_14_09.929_511_780.png': 'Detritos',
 'frame_119_2017-09-21_20_54_47.206_185_157.png': 'Detritos',
 'frame_441_2017-09-16_01_09_39.011_311_812.png': 'Detritos',
 'frame_154_2017-09-20_19_41_19.269_1582_1099.png': 'Detritos',
 'frame_253_2017-09-23_00_10_41.055_997_521.png': 'Detritos',
 'frame_1_2017-09-21_06_15_38.060_1916_1528.png': 'Detritos',
 'frame_933_2017-09-21_00_08_23.959_215_1694.png': 'Detritos',
 'frame_596_2017-09-21_20_54_47.206_1877_1323.png': 'Detritos',
 'frame_930_2017-09-20_15_36_29.632_1611_1595.png': 'Detritos',
 'frame_123_2017-09-16_20_53_26.537_1570_1091.png': 'Detritos',
 'frame_281_2017-09-20_20_59_12.793_1131_878.png': 'Detritos',
 'frame_483_2017-09-17_08_52_09.774_249_1532.png': 'Detritos',
 'frame_474_2017-09-16_16_18_38.403_1336_448.png': 'Detritos',
 'frame_418_2017-09-20_18_56_48.413_616_1790.png': 'Detritos',
 'frame_631_2017-09-30_00_19_26.844_257_1040.png': 'Detritos',
 'frame_503_2017-09-16_01_09_39.011_569_783.png': 'Detritos',
 'frame_640_2017-10-06_20_57_23.135_264_1262.png': 'Detritos',
 'frame_633_2017-09-24_00_06_17.008_1851_1201.png': 'Detritos',
 'frame_184_2017-09-29_12_04_58.884_1168_1135.png': 'Detritos',
 'frame_922_2017-09-22_06_00_04.648_1639_360.png': 'Detritos',
 'frame_515_2017-09-25_18_07_41.978_413_1450.png': 'Detritos',
 'frame_928_2017-09-20_23_57_16.170_911_426.png': 'Detritos',
 'frame_595_2017-09-21_05_31_06.977_1824_1721.png': 'Detritos',
 'frame_925_2017-09-20_15_36_29.632_1303_854.png': 'Detritos',
 'frame_300_2017-09-21_23_41_42.650_1182_38.png': 'Detritos',
 'frame_606_2017-09-21_01_26_17.933_68_27.png': 'Detritos',
 'frame_331_2017-09-20_23_46_08.531_1935_1153.png': 'Detritos',
 'frame_233_2017-09-22_18_03_26.967_270_873.png': 'Detritos',
 'frame_175_2017-09-21_18_07_51.879_439_652.png': 'Detritos',
 'frame_899_2017-09-20_23_57_16.170_193_1315.png': 'Detritos',
 'frame_599_2017-09-22_11_56_11.306_46_609.png': 'Detritos',
 'frame_781_2017-09-21_18_07_51.879_327_1548.png': 'Detritos',
 'frame_912_2017-09-21_00_08_23.959_271_417.png': 'Detritos',
 'frame_927_2017-09-20_15_36_29.632_994_1199.png': 'Detritos',
 'frame_79_2017-09-16_02_13_04.215_VIDEOALE_1611_1624.png': 'Detritos',
 'frame_410_2017-09-20_23_01_37.642_364_1850.png': 'Detritos',
 'frame_905_2017-09-22_03_57_39.662_1510_139.png': 'Detritos',
 'frame_822_2017-09-23_12_02_54.587_681_1258.png': 'Detritos',
 'frame_810_2017-09-16_00_06_14.278_1610_522.png': 'Detritos',
 'frame_914_2017-09-22_03_57_39.662_837_430.png': 'Detritos',
 'frame_324_2017-09-17_00_03_41.880_1471_1669.png': 'Detritos',
 'frame_372_2017-09-16_02_13_04.215_VIDEOALE_703_177.png': 'Detritos',
 'frame_433_2017-09-21_00_08_23.959_169_742.png': 'Detritos',
 'frame_881_2017-09-23_00_10_41.055_675_1785.png': 'Detritos',
 'frame_444_2017-09-16_01_09_39.011_1722_454.png': 'Detritos',
 'frame_343_2017-09-21_09_35_56.784_391_1123.png': 'Detritos',
 'frame_375_2017-09-19_01_44_17.054_436_585.png': 'Detritos',
 'frame_174_2017-09-18_16_55_49.058_1585_106.png': 'Detritos',
 'frame_686_2017-09-22_03_57_39.662_16_1414.png': 'Detritos',
 'frame_821_2017-09-20_23_01_37.642_1623_1244.png': 'Detritos',
 'frame_201_2017-09-19_11_15_03.115_511_1751.png': 'Detritos',
 'frame_483_2017-09-21_21_39_17.997_1082_1268.png': 'Detritos',
 'frame_125_2017-09-16_03_58_45.702_51_429.png': 'Detritos',
 'frame_221_2017-09-18_08_07_19.921_715_1783.png': 'Detritos',
 'frame_29_2017-10-06_20_57_23.135_1816_0.png': 'Detritos',
 'frame_758_2017-09-30_12_00_31.607_1469_1106.png': 'Detritos',
 'frame_666_2017-09-21_14_14_09.929_131_38.png': 'Detritos',
 'frame_498_2017-09-16_17_00_55.318_1012_22.png': 'Detritos',
 'frame_956_2017-09-20_18_01_09.974_125_816.png': 'Detritos',
 'frame_799_2017-09-22_18_03_26.967_860_5.png': 'Detritos',
 'frame_920_2017-09-22_06_00_04.648_307_513.png': 'Detritos',
 'frame_190_2017-09-25_18_07_41.978_256_580.png': 'Detritos',
 'frame_675_2017-09-22_11_56_11.306_475_228.png': 'Detritos',
 'frame_482_2017-09-17_08_52_09.774_135_1808.png': 'Detritos',
 'frame_253_2017-09-21_19_36_53.362_1191_555.png': 'Detritos',
 'frame_630_2017-09-20_23_57_16.170_893_1861.png': 'Detritos',
 'frame_938_2017-09-20_23_57_16.170_92_1248.png': 'Detritos',
 'frame_331_2017-09-30_06_04_25.087_1378_674.png': 'Detritos',
 'frame_541_2017-09-17_22_57_43.580_626_1889.png': 'Detritos',
 'frame_801_2017-09-23_00_10_41.055_1655_1912.png': 'Detritos',
 'frame_337_2017-09-21_23_41_42.650_1358_627.png': 'Detritos',
 'frame_177_2017-09-28_18_05_31.581_357_363.png': 'Detritos',
 'frame_676_2017-09-20_18_56_48.413_442_1630.png': 'Detritos',
 'frame_620_2017-09-16_03_16_29.254_1080_221.png': 'Detritos',
 'frame_273_2017-09-19_18_17_50.600_846_1323.png': 'Detritos',
 'frame_374_2017-09-16_01_09_39.011_849_301.png': 'Detritos',
 'frame_97_2017-09-18_09_53_01.896_879_1020.png': 'Detritos',
 'frame_121_2017-09-20_23_46_08.531_200_1100.png': 'Detritos',
 'frame_332_2017-09-22_03_57_39.662_1890_0.png': 'Detritos',
 'frame_349_2017-09-20_16_21_00.715_746_234.png': 'Detritos',
 'frame_802_2017-09-20_18_01_09.974_892_1040.png': 'Detritos',
 'frame_464_2017-09-21_06_49_00.820_1748_5.png': 'Detritos',
 'frame_180_2017-09-30_06_04_25.087_472_318.png': 'Detritos',
 'frame_965_2017-09-20_15_36_29.632_1747_1135.png': 'Detritos',
 'frame_145_2017-09-18_22_55_10.980_1527_1649.png': 'Detritos',
 'frame_823_2017-09-20_23_01_37.642_743_25.png': 'Detritos',
 'frame_127_2017-09-24_11_58_30.642_1040_1936.png': 'Detritos',
 'frame_801_2017-09-22_11_56_11.306_794_1989.png': 'Detritos',
 'frame_714_2017-09-20_21_43_43.740_1595_1093.png': 'Detritos',
 'frame_578_2017-09-16_01_09_39.011_257_0.png': 'Detritos',
 'frame_235_2017-09-17_21_54_18.614_537_76.png': 'Detritos',
 'frame_384_2017-09-18_04_57_05.704_1768_1162.png': 'Detritos',
 'frame_402_2017-10-06_20_57_23.135_797_278.png': 'Detritos',
 'frame_914_2017-09-23_06_06_47.168_817_61.png': 'Detritos',
 'frame_31_2017-09-19_11_15_03.115_1600_631.png': 'Detritos',
 'frame_350_2017-09-20_19_41_19.269_539_0.png': 'Detritos',
 'frame_590_2017-09-16_18_04_20.306_854_956.png': 'Detritos',
 'frame_186_2017-09-17_09_55_34.504_116_905.png': 'Detritos',
 'frame_901_2017-09-23_00_10_41.055_343_1920.png': 'Detritos',
 'frame_936_2017-09-20_23_57_16.170_214_1529.png': 'Detritos',
 'frame_635_2017-09-24_11_58_30.642_1377_957.png': 'Detritos',
 'frame_902_2017-09-21_21_39_17.997_1166_1001.png': 'Detritos',
 'frame_432_2017-09-21_20_54_47.206_1444_363.png': 'Detritos',
 'frame_409_2017-09-16_01_09_39.011_58_124.png': 'Detritos',
 'frame_559_2017-09-29_18_01_05.556_1113_1206.png': 'Detritos',
 'frame_344_2017-09-28_18_05_31.581_51_0.png': 'Detritos',
 'frame_893_2017-09-21_12_00_37.243_0_1202.png': 'Detritos',
 'frame_347_2017-09-25_12_00_27.035_1066_212.png': 'Detritos',
 'frame_353_2017-09-17_21_12_02.320_1952_878.png': 'Detritos',
 'frame_540_2017-09-16_01_09_39.011_345_0.png': 'Detritos',
 'frame_294_2017-09-21_20_54_47.206_1832_1598.png': 'Detritos',
 'frame_492_2017-09-21_20_54_47.206_882_300.png': 'Detritos',
 'frame_190_2017-09-16_11_01_32.735_1515_1317.png': 'Detritos',
 'frame_356_2017-09-19_21_06_57.369_759_101.png': 'Detritos',
 'frame_139_2017-09-19_11_57_19.930_526_1059.png': 'Detritos',
 'frame_130_2017-09-24_11_58_30.642_191_1973.png': 'Detritos',
 'frame_924_2017-09-20_15_36_29.632_1506_601.png': 'Detritos',
 'frame_898_2017-09-20_18_01_09.974_735_1910.png': 'Detritos',
 'frame_797_2017-09-22_03_57_39.662_785_414.png': 'Detritos',
 'frame_457_2017-09-21_22_57_12.103_1702_907.png': 'Detritos',
 'frame_783_2017-09-20_18_56_48.413_1441_500.png': 'Detritos',
 'frame_192_2017-09-19_08_25_56.024_1661_1406.png': 'Detritos',
 'frame_451_2017-09-21_04_13_13.353_1352_1225.png': 'Detritos',
 'frame_601_2017-09-20_21_43_43.740_406_844.png': 'Detritos',
 'frame_191_2017-09-21_01_26_17.933_1505_1480.png': 'Detritos',
 'frame_338_2017-09-19_10_32_46.066_1202_865.png': 'Detritos',
 'frame_373_2017-09-16_01_09_39.011_293_50.png': 'Detritos',
 'frame_229_2017-09-19_10_32_46.066_1395_804.png': 'Detritos',
 'frame_982_2017-09-20_15_36_29.632_926_1372.png': 'Detritos',
 'frame_331_2017-09-16_01_09_39.011_1476_493.png': 'Detritos',
 'frame_90_2017-09-22_06_00_04.648_1168_1256.png': 'Detritos',
 'frame_126_2017-09-20_18_56_48.413_290_1472.png': 'Detritos',
 'frame_675_2017-09-21_04_46_36.462_15_599.png': 'Detritos',
 'frame_272_2017-09-21_11_27_13.664_1826_796.png': 'Detritos',
 'frame_196_2017-09-24_18_05_45.523_1467_743.png': 'Detritos',
 'frame_224_2017-09-18_04_57_05.704_93_767.png': 'Detritos',
 'frame_274_2017-09-18_01_04_34.024_854_1449.png': 'Detritos',
 'frame_120_2017-09-18_23_58_35.584_1403_690.png': 'Detritos',
 'frame_968_2017-09-20_18_01_09.974_1362_1231.png': 'Detritos',
 'frame_863_2017-09-20_18_23_25.361_1255_0.png': 'Detritos',
 'frame_927_2017-09-20_23_57_16.170_72_951.png': 'Detritos',
 'frame_926_2017-09-21_02_55_19.170_1063_577.png': 'Detritos',
 'frame_688_2017-09-16_02_13_04.215_VIDEOALE_1543_1576.png': 'Detritos',
 'frame_376_2017-09-19_09_50_29.580_1243_661.png': 'Detritos',
 'frame_984_2017-09-20_15_36_29.632_1271_1980.png': 'Detritos',
 'frame_687_2017-09-22_03_57_39.662_915_1177.png': 'Detritos',
 'frame_731_2017-09-21_02_55_19.170_0_700.png': 'Detritos',
 'frame_526_2017-09-18_16_55_49.058_981_568.png': 'Detritos',
 'frame_927_2017-09-22_06_00_04.648_861_824.png': 'Detritos',
 'frame_336_2017-10-06_20_57_23.135_1936_923.png': 'Detritos',
 'frame_476_2017-09-18_01_04_34.024_284_1114.png': 'Detritos',
 'frame_383_2017-09-17_16_58_22.104_919_252.png': 'Detritos',
 'frame_234_2017-10-06_20_57_23.135_1544_1739.png': 'Detritos',
 'frame_931_2017-09-20_15_36_29.632_173_652.png': 'Detritos',
 'frame_447_2017-09-16_15_15_13.245_1097_790.png': 'Detritos',
 'frame_748_2017-09-20_23_57_16.170_989_1730.png': 'Detritos',
 'frame_477_2017-09-28_18_05_31.581_443_626.png': 'Detritos',
 'frame_924_2017-09-20_15_36_29.632_1649_586.png': 'Detritos',
 'frame_164_2017-09-22_18_03_26.967_0_599.png': 'Detritos',
 'frame_919_2017-09-20_23_57_16.170_1483_57.png': 'Detritos',
 'frame_475_2017-09-16_21_56_51.690_994_1487.png': 'Detritos',
 'frame_797_2017-09-30_00_19_26.844_514_822.png': 'Detritos',
 'frame_507_2017-09-16_01_09_39.011_862_545.png': 'Detritos',
 'frame_458_2017-09-21_06_15_38.060_1805_782.png': 'Detritos',
 'frame_242_2017-09-18_13_03_16.745_161_542.png': 'Detritos',
 'frame_558_2017-09-25_05_57_58.288_1771_730.png': 'Detritos',
 'frame_630_2017-09-25_00_01_52.236_1843_0.png': 'Detritos',
 'frame_813_2017-09-21_02_10_48.705_1949_697.png': 'Detritos',
 'frame_395_2017-09-17_02_10_31.042_648_442.png': 'Detritos',
 'frame_424_2017-09-19_03_51_07.404_1166_720.png': 'Detritos',
 'frame_107_2017-09-16_15_15_13.245_129_1675.png': 'Detritos',
 'frame_175_2017-09-18_16_55_49.058_1932_58.png': 'Detritos',
 'frame_635_2017-09-27_00_10_30.061_1087_56.png': 'Detritos',
 'frame_59_2017-09-18_02_07_59.208_1221_80.png': 'Detritos',
 'frame_970_2017-09-20_18_23_25.361_408_17.png': 'Detritos',
 'frame_137_2017-09-16_23_00_16.100_1377_1127.png': 'Detritos',
 'frame_152_2017-09-19_08_25_56.024_1165_1669.png': 'Detritos',
 'frame_459_2017-09-21_22_57_12.103_890_688.png': 'Detritos',
 'frame_808_2017-09-24_06_02_23.018_1629_1858.png': 'Detritos',
 'frame_826_2017-09-20_17_05_31.514_261_297.png': 'Detritos',
 'frame_591_2017-09-16_18_04_20.306_1383_793.png': 'Detritos',
 'frame_9_2017-09-19_16_53_16.639_508_1110.png': 'Detritos',
 'frame_152_2017-09-16_01_09_39.011_1920_1089.png': 'Detritos',
 'frame_256_2017-09-19_08_25_56.024_114_1493.png': 'Detritos',
 'frame_401_2017-09-19_04_33_23.799_15_1251.png': 'Detritos',
 'frame_904_2017-09-23_12_02_54.587_1641_1702.png': 'Detritos',
 'frame_558_2017-09-19_09_50_29.580_107_29.png': 'Detritos',
 'frame_484_2017-09-17_08_52_09.774_536_1382.png': 'Detritos',
 'frame_903_2017-09-21_12_00_37.243_1942_64.png': 'Detritos',
 'frame_719_2017-10-06_20_57_23.135_568_1762.png': 'Detritos',
 'frame_286_2017-09-27_12_02_43.349_683_1793.png': 'Detritos',
 'frame_945_2017-09-21_00_08_23.959_798_1127.png': 'Detritos',
 'frame_603_2017-09-21_11_27_13.664_1634_594.png': 'Detritos',
 'frame_791_2017-09-22_06_00_04.648_840_480.png': 'Detritos',
 'frame_801_2017-09-20_17_38_54.681_651_1678.png': 'Detritos',
 'frame_321_2017-09-21_20_54_47.206_1406_597.png': 'Detritos',
 'frame_158_2017-09-21_02_55_19.170_1556_1703.png': 'Detritos',
 'frame_926_2017-09-20_15_36_29.632_1125_1056.png': 'Detritos',
 'frame_232_2017-09-19_00_19_43.344_1727_1365.png': 'Detritos',
 'frame_474_2017-09-16_21_56_51.690_946_1341.png': 'Detritos',
 'frame_943_2017-09-20_15_36_29.632_926_1394.png': 'Detritos',
 'frame_579_2017-09-29_05_57_44.317_1794_238.png': 'Detritos',
 'frame_636_2017-09-25_18_07_41.978_46_1002.png': 'Detritos',
 'frame_383_2017-09-18_04_57_05.704_1954_1012.png': 'Detritos',
 'frame_188_2017-09-28_06_02_10.259_1987_775.png': 'Detritos',
 'frame_331_2017-09-16_11_01_32.735_304_768.png': 'Detritos',
 'frame_26_2017-09-18_00_01_08.787_1165_263.png': 'Detritos',
 'frame_291_2017-09-22_18_03_26.967_1930_1091.png': 'Detritos',
 'frame_934_2017-09-20_18_01_09.974_391_1172.png': 'Detritos',
 'frame_12_2017-09-21_09_35_56.784_156_12.png': 'Detritos',
 'frame_730_2017-09-16_02_13_04.215_VIDEOALE_1560_643.png': 'Detritos',
 'frame_261_2017-09-19_03_08_50.128_414_1589.png': 'Detritos',
 'frame_897_2017-09-20_23_57_16.170_202_322.png': 'Detritos',
 'frame_299_2017-09-24_11_58_30.642_451_1247.png': 'Detritos',
 'frame_591_2017-09-16_18_04_20.306_942_882.png': 'Detritos',
 'frame_687_2017-09-21_10_09_19.640_1094_899.png': 'Detritos',
 'frame_332_2017-09-30_06_04_25.087_1215_1287.png': 'Detritos',
 'frame_405_2017-09-16_03_16_29.254_1455_477.png': 'Detritos',
 'frame_583_2017-09-21_13_29_38.934_414_1520.png': 'Detritos',
 'frame_125_2017-09-16_20_53_26.537_675_1051.png': 'Detritos',
 'frame_277_2017-09-16_18_04_20.306_1372_964.png': 'Detritos',
 'frame_593_2017-09-19_01_02_00.347_652_97.png': 'Detritos',
 'frame_287_2017-09-21_22_23_48.887_1051_183.png': 'Detritos',
 'frame_345_2017-09-18_02_07_59.208_1245_1130.png': 'Detritos',
 'frame_86_2017-09-20_20_59_12.793_1344_802.png': 'Detritos',
 'frame_468_2017-09-19_12_18_28.114_582_1154.png': 'Detritos',
 'frame_168_2017-09-21_09_35_56.784_1904_770.png': 'Detritos',
 'frame_969_2017-09-20_18_01_09.974_1636_1148.png': 'Detritos',
 'frame_332_2017-09-19_06_19_05.639_1637_1684.png': 'Detritos',
 'frame_140_2017-09-19_11_57_19.930_322_453.png': 'Detritos',
 'frame_981_2017-09-20_20_25_49.768_55_632.png': 'Detritos',
 'frame_139_2017-09-25_00_01_52.236_1781_1088.png': 'Detritos',
 'frame_665_2017-09-21_20_21_24.131_457_1433.png': 'Detritos',
 'frame_201_2017-09-21_06_15_38.060_957_952.png': 'Detritos',
 'frame_38_2017-09-21_04_46_36.462_439_1361.png': 'Detritos',
 'frame_458_2017-09-20_21_43_43.740_1734_237.png': 'Detritos',
 'frame_913_2017-09-21_00_08_23.959_507_268.png': 'Detritos',
 'frame_727_2017-09-20_18_56_48.413_1627_1170.png': 'Detritos',
 'frame_62_2017-09-17_09_55_34.504_274_392.png': 'Detritos',
 'frame_806_2017-09-20_18_56_48.413_161_1436.png': 'Detritos',
 'frame_142_2017-09-21_01_26_17.933_988_142.png': 'Detritos',
 'frame_476_2017-09-22_18_03_26.967_0_1180.png': 'Detritos',
 'frame_957_2017-09-20_18_01_09.974_269_964.png': 'Detritos',
 'frame_53_2017-09-21_02_55_19.170_433_960.png': 'Detritos'}

def find_coordinates(df, name):
    for i, n in enumerate(df['File']):
        if get_file_name(n) == name:
            return df['densenet_x'][i+1], df['densenet_y'][i+1]
    return None, None

def add_reviewed_to_fig(df, fig):
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
        x, y = find_coordinates(df, key)
        if x == None:
            continue
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
                ), name=reviewed_label_map['Indefinido']),
                secondary_y=True,
            )

    fig.add_trace(
            go.Scatter(x=detritos['x'], y=detritos['y'], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Detritos'],
                    size=8,
                    colorscale='Hot',
                ), name=reviewed_label_map['Detritos']),
                secondary_y=True,
            )

    fig.add_trace(
            go.Scatter(x=plancton['x'], y=plancton['y'], opacity=0.8,  mode='markers', marker=dict(
                    color=reviewed_color_map['Plancton'],
                    size=8,
                    colorscale='Hot',
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

    #remove second column in DataFrame
    cols.remove(8)

    df = df.iloc[:, cols]

    color=[df['Ground Truth'][i + 1] for i in range(len(df['Ground Truth']))]

    color_prediction=[]

    for i, label in enumerate(df['Ground Truth']):
        if df['DenseNet'][i+1] == 'Y':
            color_prediction.append(label)
        else:
            color_prediction.append(inverse[label])

        coord_tuple = (df['densenet_x'][i + 1], df['densenet_y'][i + 1])
        if coord_tuple not in image_coord_dict:
            image_coord_dict[coord_tuple] = get_file_name(df['File'][i + 1])

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
    go.Scatter(x=df['densenet_x'].to_numpy(), y=df['densenet_y'].to_numpy(), opacity=0.1, mode='markers', marker=dict(
            color=[prediction_color_discrete_map[x] for x in color_prediction],
            size=8,
            colorscale='Hot',
        ), name="Prediction labels"),
        secondary_y=True,
    )

    fig.add_trace(
    go.Scatter(x=df4_1[mx], y=df4_1[my], opacity=1.0,  mode='markers', marker=dict(
            color=df4_1['color'],
            size=10,
            colorscale='Hot',
        ), name="4/4 error on classification"),
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
            ), name="4/4 error on classification and K neighbors different"),
        secondary_y=True,
    )

    add_reviewed_to_fig(df, fig)

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
    # Logic to determine image path based on x, y coordinates
    # Example path, adjust according to your logic
    image_name = image_coord_dict.get((x,y), "not_exist")
    image_path = 'static/images_resized/' + image_name  # Adjust this path as necessary

    print(x, y)
    print(image_path)

    # Check if the file exists
    if os.path.isfile('app/'+image_path):
        return jsonify({"imagePath": '/' + image_path, "exists": True})
    else:
        return jsonify({"message": "Image not available", "exists": False})
