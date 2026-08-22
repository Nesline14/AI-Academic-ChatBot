from app.models.user import User
from app.models.academic import Department, Course, Subject, ClassRoom, ClassStudent, ClassSchedule
from app.models.attendance import Attendance
from app.models.result import Result
from app.models.announcement import Announcement
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.event import CampusEvent, EventRegistration
from app.models.project import AcademicProject, ProjectMember
from app.models.club import Club, ClubMember, ClubActivity
from app.models.notification import Notification
from app.models.chatbot import ChatMessage

__all__ = [
    'User',
    'Department',
    'Course',
    'Subject',
    'ClassRoom',
    'ClassStudent',
    'ClassSchedule',
    'Attendance',
    'Result',
    'Announcement',
    'Assignment',
    'AssignmentSubmission',
    'CampusEvent',
    'EventRegistration',
    'AcademicProject',
    'ProjectMember',
    'Club',
    'ClubMember',
    'ClubActivity',
    'Notification',
    'ChatMessage'
]
