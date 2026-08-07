"""
==============================================================================
Backend Integration Verification Suite
==============================================================================
Tests Flask endpoints, database queries, and ML prediction services.
==============================================================================
"""

import os
import sys
import unittest
import json

# Add BASE_DIR to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.app import app

class BackendTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_landing_page(self):
        """Test landing page route GET /"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_02_login_page(self):
        """Test login page route GET /login"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_03_dashboard_page(self):
        """Test dashboard page route GET /dashboard"""
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_04_healing_prediction_api(self):
        """Test ANN healing prediction endpoint POST /api/healing-prediction"""
        payload = {
            "age": 35,
            "fracture_type": "Transverse",
            "bone": "Wrist",
            "smoking": False,
            "diabetes": False,
            "severity": "Moderate"
        }
        response = self.app.post('/api/healing-prediction',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('estimated_weeks', data)

    def test_05_rehab_recommendation_api(self):
        """Test rehab recommendation endpoint POST /api/rehab-recommendation"""
        payload = {
            "prediction": "Fractured",
            "severity": "Moderate",
            "confidence": 88.5
        }
        response = self.app.post('/api/rehab-recommendation',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('plan', data)

    def test_06_nearby_doctors_api(self):
        """Test nearby doctors endpoint GET /api/nearby-doctors"""
        response = self.app.get('/api/nearby-doctors?lat=16.7&lng=74.4')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(len(data['doctors']) > 0)

    def test_07_dashboard_stats_api(self):
        """Test dashboard aggregate stats endpoint GET /api/dashboard"""
        response = self.app.get('/api/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_08_history_api(self):
        """Test history list endpoint GET /api/history"""
        response = self.app.get('/api/history')
        self.assertEqual(response.status_code, 200)

    def test_09_predict_image_api(self):
        """Test primary prediction endpoint POST /predict"""
        import io
        import glob
        test_images = glob.glob(os.path.join(BASE_DIR, 'Bone_Fracture_Dataset', 'test', '*', '*'))
        if test_images:
            sample_path = test_images[0]
            with open(sample_path, 'rb') as f:
                data = {
                    'file': (io.BytesIO(f.read()), os.path.basename(sample_path)),
                    'patient_name': 'Test Patient'
                }
                response = self.app.post('/predict', data=data, content_type='multipart/form-data')
                self.assertEqual(response.status_code, 200)
                res_json = response.get_json()
                self.assertEqual(res_json['status'], 'success')
                self.assertIn('prediction', res_json)
                self.assertIn('confidence', res_json)

if __name__ == '__main__':
    unittest.main()
