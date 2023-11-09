import json
import numpy as np
import h5py
import pickle as pk
from PIL import Image

from keras.models import load_model
from keras.preprocessing.image import img_to_array, load_img
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing import image
from keras.models import Model
import tensorflow as tf


def prepare_img_224(img_path):
    img = load_img(img_path, target_size=(224,224))
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x

with open('static/cat_counter.pk','rb') as f:
    cat_counter = pk.load(f)


cat_list = [k for k, v in cat_counter.most_common()[:27]]


global graph
graph = tf.compat.v1.get_default_graph()  # to restore the graph after saving it

def prepare_flat(img_224):
    base_model = load_model('static/vgg16.h5')
    model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)
    feature = model.predict(img_224)
    flat = feature.flatten()
    flat = np.expand_dims(flat, axis=0)

    return flat

CLASS_INDEX_PATH = 'static/imagenet_class_index.json'

def get_predictions(preds,top=5):
    global CLASS_INDEX
    
    CLASS_INDEX = json.load(open(CLASS_INDEX_PATH))
    
    results = []
    for pred in preds:
        top_indices = pred.argsort()[-top:][::-1]
        result = [tuple(CLASS_INDEX[str(i)]) + (pred[i],) for i in top_indices]
        result.sort(key=lambda x: x[2], reverse=True)
        results.append(result)
    return results

def car_categories_check(img_224):
    first_check = load_model('static/vgg16.h5')
    print("Checking if a Car..")
    out = first_check.predict(img_224)
    top = get_predictions(out, top=5)
    
    for j in top[0]:
        if j[0:2] in cat_list:
            print("Car Check Passed !\n")
            return True
    return False

def car_damage_check(img_flat):
    second_check = pk.load(open('static/second_classifier.pickle', 'rb'))

    print("Checking if there is a damage...")
  
    train_labels = ['00-damage', '01-whole']
    preds = second_check.predict(img_flat)
    predictions = train_labels[preds[0]]
    
    if train_labels[preds[0]] == '00-damage':
        print("completed - proceeding to location and severity determination\n")
        return True
    return False

def location_assesment(img_flat):
    print("Validating the damage area - Front, Rear or Side")
    third_check = pk.load(open('static/third_classifier.pickle', 'rb'))
    train_labels = ['Front', 'Rear', 'Side']
    
    preds = third_check.predict(img_flat)
    predictions = train_labels[preds[0]]
    
    print("Your car is damaged at - " + train_labels[preds[0]])
    print("Location assesment complete")
    print('\n')
    return predictions

def severity_assesment(img_flat):
    print("Validating the Severity...")
    fourth_check = pk.load(open('static/fourth_classifier.pickle', 'rb'))
    train_labels = ['Minor', 'Moderate', 'Severe']
    
    preds = fourth_check.predict(img_flat)
    predictions = train_labels[preds[0]]
    print("Your Car impact is - " + train_labels[preds[0]])
    print("Severity assesment complete")
    print('\n')
    return predictions


