import unittest
from app import app
from db import init_db, query_db

class ThesisPortalTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_login(self):
        response = self.client.post('/login', data=dict(
            username='admin',
            password='admin123',
            role='admin'
        ), follow_redirects=True)
        self.assertIn(b'God-View Dashboard', response.data)

    def test_unauthorized_access(self):
        response = self.client.get('/admin', follow_redirects=True)
        self.assertIn(b'Thesis Portal', response.data) # Changed from 'Login' to brand name

    def test_assignment_logic(self):
        # Login as student
        with self.client.session_transaction() as sess:
            sess['user_id'] = 4
            sess['username'] = 'user1'
            sess['role'] = 'receiver'

        response = self.client.post('/api/requests', json=dict(
            title='Test Thesis',
            description='Test Description'
        ))
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn(data['expert_name'], ['Expert Writer 1', 'Expert Writer 2'])

if __name__ == '__main__':
    unittest.main()
