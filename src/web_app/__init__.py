from flask import Flask, request, render_template, url_for, redirect
import numpy as np
import pandas as pd
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.backend import clear_session
from tensorflow import keras


clear_session()
model = keras.models.load_model('model_four_class_v2/', compile=False)
opt = Adam(lr=0.0000001)
model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

UPLOAD_FOLDER = 'static/testing_data/upload_images'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Form page to submit text
@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    for f in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, f))
    if request.method == 'POST':
        
        file = request.files['file']
        filename = file.filename.replace(' ', '')
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('predict',filename=filename))

    return render_template('index.html')


# My prediction app
@app.route('/prediction/<filename>')
def predict(filename):
    generator = ImageDataGenerator(fill_mode='nearest', featurewise_center=True)
    genny = generator.flow_from_directory('static/testing_data', (224,224), class_mode='categorical', batch_size=1)
    y = model.predict_generator(genny)
    label_num = np.argsort(y[0])[-1]
    if label_num == 0:
        category = 'Bulk Bricks'
    elif label_num == 1:
        category = 'Young Childrens'
    elif label_num == 2:
        category = 'MiniFig'
    else:
        category = 'Technic / Bionic'
    confidence = round(max(y[0])*100, 1)
    file_path = f'../static/testing_data/upload_images/{filename}'

    

    
    return render_template('prediction.html', category=category, confidence=confidence, filepath=file_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



