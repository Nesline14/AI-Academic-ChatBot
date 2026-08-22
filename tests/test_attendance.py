import unittest
from datetime import date
from app import create_app
from extensions import db
from app.models.user import User
from app.models.academic import Department, Subject, ClassRoom
from app.models.attendance import Attendance
from app.services.attendance_service import get_student_attendance_summary


class AttendanceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed minimal data
        self.dept = Department(code='CSE', name='Computer Science')
        db.session.add(self.dept)
        db.session.flush()

        self.student = User(email='alex@example.com', full_name='Alex Rivers', role='student')
        self.student.set_password('Pass123!')
        self.teacher = User(email='prof@example.com', full_name='Prof Thorne', role='teacher')
        self.teacher.set_password('Pass123!')
        db.session.add_all([self.student, self.teacher])
        db.session.flush()

        self.subject = Subject(code='CS-101', name='Intro to CS', department_id=self.dept.id, semester=1, credits=4)
        self.classroom = ClassRoom(name='CSE-1A', code='CSE-1A', department_id=self.dept.id, semester=1, section='A', academic_year='2026')
        db.session.add_all([self.subject, self.classroom])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_attendance_summary_calculation(self):
        # Add 3 present, 1 absent
        for i in range(3):
            att = Attendance(student_id=self.student.id, class_id=self.classroom.id, subject_id=self.subject.id, date=date(2026, 3, i + 1), status='Present', marked_by_id=self.teacher.id)
            db.session.add(att)
        att_abs = Attendance(student_id=self.student.id, class_id=self.classroom.id, subject_id=self.subject.id, date=date(2026, 3, 4), status='Absent', marked_by_id=self.teacher.id)
        db.session.add(att_abs)
        db.session.commit()

        summary = get_student_attendance_summary(self.student.id)
        self.assertEqual(summary['total_classes'], 4)
        self.assertEqual(summary['attended'], 3)
        self.assertEqual(summary['missed'], 1)
        self.assertEqual(summary['overall_percentage'], 75.0)
        self.assertFalse(summary['is_below_threshold'])


if __name__ == '__main__':
    unittest.main()
