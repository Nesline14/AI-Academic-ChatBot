import unittest
from app import create_app
from extensions import db
from app.models.user import User
from app.models.academic import Department, Subject, ClassRoom
from app.models.result import Result
from app.services.result_service import get_student_academic_summary


class ResultsTestCase(unittest.TestCase):
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

    def test_grade_calculation(self):
        grade, points = Result.calculate_grade_and_gpa(95, 100)
        self.assertEqual(grade, 'A+')
        self.assertEqual(points, 10.0)

        grade, points = Result.calculate_grade_and_gpa(85, 100)
        self.assertEqual(grade, 'A')
        self.assertEqual(points, 9.0)

        grade, points = Result.calculate_grade_and_gpa(35, 100)
        self.assertEqual(grade, 'F')
        self.assertEqual(points, 0.0)

    def test_student_academic_summary(self):
        dept = Department(code='CSE', name='Computer Science')
        db.session.add(dept)
        db.session.flush()

        student = User(email='student@example.com', full_name='Student User', role='student')
        student.set_password('Pass123!')
        db.session.add(student)
        db.session.flush()

        classroom = ClassRoom(name='CSE-1A', code='CSE-1A', department_id=dept.id, semester=1, section='A', academic_year='2026')
        db.session.add(classroom)
        db.session.flush()

        sub1 = Subject(code='CS-101', name='Subject 1', department_id=dept.id, semester=1, credits=4)
        sub2 = Subject(code='CS-102', name='Subject 2', department_id=dept.id, semester=1, credits=4)
        db.session.add_all([sub1, sub2])
        db.session.flush()

        r1 = Result(student_id=student.id, subject_id=sub1.id, class_id=classroom.id, semester=1, internal_marks=28, assignment_marks=20, exam_marks=42, total_marks=90, max_marks=100, grade='A+', gpa_points=10.0)
        r2 = Result(student_id=student.id, subject_id=sub2.id, class_id=classroom.id, semester=1, internal_marks=25, assignment_marks=18, exam_marks=37, total_marks=80, max_marks=100, grade='A', gpa_points=9.0)
        db.session.add_all([r1, r2])
        db.session.commit()

        summary = get_student_academic_summary(student.id)
        self.assertEqual(summary['cgpa'], 9.5)
        self.assertEqual(summary['passed_subjects'], 2)


if __name__ == '__main__':
    unittest.main()
