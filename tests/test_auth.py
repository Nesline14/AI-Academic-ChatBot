import unittest
from app import create_app
from extensions import db
from app.models.user import User


class AuthTestCase(unittest.TestCase):
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

    def test_password_hashing(self):
        u = User(email='test@example.com', full_name='Test User', role='student')
        u.set_password('Secret123!')
        self.assertTrue(u.check_password('Secret123!'))
        self.assertFalse(u.check_password('WrongPassword'))

    def test_login_and_logout(self):
        u = User(email='student1@example.com', full_name='Student One', role='student')
        u.set_password('Password123!')
        db.session.add(u)
        db.session.commit()

        # Login via /auth/login
        response = self.client.post('/auth/login', data={
            'email': 'student1@example.com',
            'password': 'Password123!'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Logout via /auth/logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
