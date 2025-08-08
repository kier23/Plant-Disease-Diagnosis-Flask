from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime

PREDICTIONS_FILE = "predictions.json"

predictions_api = Blueprint("predictions_api", __name__)

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


@predictions_api.route('/predictions', methods=['GET'])
def get_predictions():
    predictions = load_predictions()
    return jsonify(predictions), 200


@predictions_api.route('/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    predictions = load_predictions()
    for pred in predictions:
        if pred["id"] == prediction_id:
            return jsonify(pred), 200
    return jsonify({"error": "Prediction not found"}), 404


@predictions_api.route('/predictions', methods=['POST'])
def create_prediction():
    predictions = load_predictions()
    data = request.get_json()


    if not data or "filename" not in data or "prediction" not in data:
        return jsonify({"error": "Missing filename or prediction"}), 400

    new_id = predictions[-1]['id'] + 1 if predictions else 1
    new_pred = {
        "id": new_id,
        "filename": data["filename"],
        "prediction": data["prediction"],
        "timestamp": datetime.now().isoformat()
    }

    predictions.append(new_pred)
    save_predictions(predictions)
    return jsonify(new_pred), 201


@predictions_api.route('/predictions/<int:prediction_id>', methods=['PUT'])
def update_prediction(prediction_id):
    predictions = load_predictions()
    for pred in predictions:
        if pred["id"] == prediction_id:
            data = request.get_json()
            pred["filename"] = data.get("filename", pred["filename"])
            pred["prediction"] = data.get("prediction", pred["prediction"])
            save_predictions(predictions)
            return jsonify(pred), 200
    return jsonify({"error": "Prediction not found"}), 404


@predictions_api.route('/predictions/<int:prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    predictions = load_predictions()
    for pred in predictions:
        if pred["id"] == prediction_id:
            predictions.remove(pred)
            save_predictions(predictions)
            return jsonify({"message": "Prediction deleted"}), 200
    return jsonify({"error": "Prediction not found"}), 404
