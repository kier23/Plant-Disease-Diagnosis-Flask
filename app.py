import os
import json
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from datetime import datetime

# Flask app
app = Flask(__name__)

from prediction import predictions_api
app.register_blueprint(predictions_api)


# Load model
model = tf.keras.models.load_model('PlantDNet.h5', compile=False)
print('Model loaded. Check http://127.0.0.1:5000/')


PREDICTIONS_FILE = "predictions.json"

def load_predictions():
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_predictions(predictions):
    with open(PREDICTIONS_FILE, "w") as f:
        json.dump(predictions, f, indent=4)

def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(64, 64))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x.astype('float32') / 255
    preds = model.predict(x)
    return preds

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get file from request
        f = request.files['file']

        # Save file to uploads folder
        basepath = os.path.dirname(__file__)
        uploads_path = os.path.join(basepath, 'uploads')
        os.makedirs(uploads_path, exist_ok=True)
        file_path = os.path.join(uploads_path, secure_filename(f.filename))
        f.save(file_path)

        # Predict
        preds = model_predict(file_path, model)
        disease_class = [
            'Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy', 'Potato___Early_blight',
            'Potato___Late_blight', 'Potato___healthy', 'Tomato_Bacterial_spot', 'Tomato_Early_blight',
            'Tomato_Late_blight', 'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot',
            'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot',
            'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus', 'Tomato_healthy'
        ]
        predicted_index = np.argmax(preds[0])
        predicted_label = disease_class[predicted_index]


        predictions = load_predictions()


        new_id = predictions[-1]['id'] + 1 if predictions else 1


        predictions.append({
            "id": new_id,
            "filename": f.filename,
            "prediction": predicted_label,
            "timestamp": datetime.now().isoformat()
        })

        save_predictions(predictions)

        return predicted_label
    return None

if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
