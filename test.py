import unittest
import json
import os
from flask import Flask
from prediction import predictions_api, PREDICTIONS_FILE

class TestPredictionsAPI(unittest.TestCase):

    def setUp(self):
        self.backup_file = None
        if os.path.exists(PREDICTIONS_FILE):
            self.backup_file = PREDICTIONS_FILE + ".bak"
            os.rename(PREDICTIONS_FILE, self.backup_file)

        with open(PREDICTIONS_FILE, "w") as f:
            json.dump([], f)

        app = Flask(__name__)
        app.register_blueprint(predictions_api)
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        """Clean up test file and restore original."""
        if os.path.exists(PREDICTIONS_FILE):
            os.remove(PREDICTIONS_FILE)
        if self.backup_file:
            os.rename(self.backup_file, PREDICTIONS_FILE)


    def test_create_prediction_positive(self):
        payload = {"filename": "leaf.jpg", "prediction": "Tomato_healthy"}
        res = self.client.post("/predictions", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["filename"], "leaf.jpg")
        self.assertEqual(data["prediction"], "Tomato_healthy")
        self.assertIn("timestamp", data)
        self.assertIn("id", data)

    def test_create_prediction_negative_missing_fields(self):
        res = self.client.post("/predictions", json={"filename": "leaf.jpg"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

    def test_get_all_predictions_positive(self):
        self.client.post("/predictions", json={"filename": "leaf.jpg", "prediction": "Tomato_healthy"})
        res = self.client.get("/predictions")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_get_all_predictions_negative_empty_list(self):
        res = self.client.get("/predictions")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), [])


    def test_get_single_prediction_positive(self):
        self.client.post("/predictions", json={"filename": "leaf.jpg", "prediction": "Tomato_healthy"})
        res = self.client.get("/predictions/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["id"], 1)

    def test_get_single_prediction_negative_not_found(self):
        res = self.client.get("/predictions/999")
        self.assertEqual(res.status_code, 404)
        self.assertIn("error", res.get_json())


    def test_update_prediction_positive(self):
        self.client.post("/predictions", json={"filename": "leaf.jpg", "prediction": "Tomato_healthy"})
        res = self.client.put("/predictions/1", json={"prediction": "Potato___Early_blight"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["prediction"], "Potato___Early_blight")

    def test_update_prediction_negative_not_found(self):
        res = self.client.put("/predictions/999", json={"prediction": "None"})
        self.assertEqual(res.status_code, 404)
        self.assertIn("error", res.get_json())


    def test_delete_prediction_positive(self):
        self.client.post("/predictions", json={"filename": "leaf.jpg", "prediction": "Tomato_healthy"})
        res = self.client.delete("/predictions/1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["message"], "Prediction deleted")

    def test_delete_prediction_negative_not_found(self):
        res = self.client.delete("/predictions/999")
        self.assertEqual(res.status_code, 404)
        self.assertIn("error", res.get_json())


if __name__ == "__main__":
    unittest.main()
