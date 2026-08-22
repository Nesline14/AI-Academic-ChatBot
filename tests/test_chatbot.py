import unittest
from app import create_app
from extensions import db
from app.models.user import User
from app.services.chatbot_service import process_student_query


class ChatbotTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.student = User(email='teststudent@example.com', full_name='Test Student', role='student')
        self.student.set_password('Pass123!')
        db.session.add(self.student)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_chatbot_greetings(self):
        res = process_student_query(self.student, "Hello campus bot")
        self.assertIn("Hello", res['response'])
        self.assertEqual(res['intent'], 'greeting')

    def test_chatbot_attendance_intent(self):
        res = process_student_query(self.student, "What is my attendance percentage?")
        self.assertEqual(res['intent'], 'attendance')
        self.assertIn("attendance", res['response'].lower())

    def test_chatbot_events_intent(self):
        res = process_student_query(self.student, "What events are happening?")
        self.assertEqual(res['intent'], 'events')
        self.assertIn("event", res['response'].lower())


if __name__ == '__main__':
    unittest.main()
