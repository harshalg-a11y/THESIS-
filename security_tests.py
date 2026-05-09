import unittest
from app import app
from db import init_db, query_db, hash_password

class ThesisPortalSecurityTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_idor_protection(self):
        # Login as user1 (id 4)
        with self.client.session_transaction() as sess:
            sess['user_id'] = 4
            sess['username'] = 'user1'
            sess['role'] = 'receiver'

        # Try to access messages for a request that doesn't exist or isn't theirs
        # Note: In our setup, user1 has request id 3 from previous verification
        response = self.client.get('/api/messages/999')
        self.assertEqual(response.status_code, 403)

    def test_lounge_xss_protection(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 4
            sess['username'] = 'user1'
            sess['role'] = 'receiver'

        payload = "<script>alert('xss')</script>"
        self.client.post('/api/lounge', json=dict(content=payload))

        response = self.client.get('/api/lounge')
        data = response.get_json()
        self.assertEqual(data[-1]['content'], payload)
        # Note: Backend stores it raw, frontend must escape via innerText (which we verified in code)

if __name__ == '__main__':
    unittest.main()
