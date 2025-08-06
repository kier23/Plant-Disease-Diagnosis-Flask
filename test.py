import unittest
import io
import os
from unittest.mock import patch, MagicMock
from app import app, db
from models.note import Note

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # --- App routes coverage ---

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data.lower())  # check html page loads

    @patch('app.model_predict')
    def test_predict_post_route(self, mock_predict):
        mock_predict.return_value = [[0.1] * 14 + [1.0]]  # force last index
        data = {
            'file': (io.BytesIO(b"fake image data"), 'test.jpg')
        }

        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        response = self.client.post('/predict', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tomato_healthy', response.data)  

    def test_predict_get_route(self):
        response = self.client.get('/predict')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'null')


    def test_create_note_success(self):
        response = self.client.post('/api/notes/', json={
            'content': 'Leaf spot detected on lower leaves.',
            'diagnosis_id': 1
        })
        self.assertEqual(response.status_code, 201)

    def test_create_note_missing_fields(self):
        response = self.client.post('/api/notes/', json={})
        self.assertEqual(response.status_code, 400)

    def test_get_note_success(self):
        with app.app_context():
            note = Note(content="Test note", diagnosis_id=1)
            db.session.add(note)
            db.session.commit()
            note_id = note.id

        response = self.client.get(f'/api/notes/{note_id}')
        self.assertEqual(response.status_code, 200)

    def test_get_note_not_found(self):
        response = self.client.get('/api/notes/999')
        self.assertEqual(response.status_code, 404)

    def test_update_note_success(self):
        with app.app_context():
            note = Note(content="Old note", diagnosis_id=1)
            db.session.add(note)
            db.session.commit()
            note_id = note.id

        response = self.client.put(f'/api/notes/{note_id}', json={
            'content': 'Updated note',
            'diagnosis_id': 1
        })
        self.assertEqual(response.status_code, 200)

    def test_update_note_not_found(self):
        response = self.client.put('/api/notes/999', json={
            'content': 'Updated note',
            'diagnosis_id': 1
        })
        self.assertEqual(response.status_code, 404)

    def test_update_note_missing_description(self):
        with app.app_context():
            note = Note(content="Old", diagnosis_id=1)
            db.session.add(note)
            db.session.commit()
            note_id = note.id

        response = self.client.put(f'/api/notes/{note_id}', json={})
        self.assertEqual(response.status_code, 400)

    def test_delete_note_success(self):
        with app.app_context():
            note = Note(content="Delete me", diagnosis_id=1)
            db.session.add(note)
            db.session.commit()
            note_id = note.id

        response = self.client.delete(f'/api/notes/{note_id}')
        self.assertEqual(response.status_code, 200)

    def test_delete_note_not_found(self):
        response = self.client.delete('/api/notes/999')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
