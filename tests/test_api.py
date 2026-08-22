import unittest
from app import create_app
from extensions import db


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_health_endpoint(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['status'], 'healthy')
        self.assertIn('CampusConnect', json_data['service'])

    def test_announcements_api(self):
        response = self.client.get('/api/announcements')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('announcements', json_data)

    def test_events_api(self):
        response = self.client.get('/api/events')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('events', json_data)


if __name__ == '__main__':
    unittest.main()
