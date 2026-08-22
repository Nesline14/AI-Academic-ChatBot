from datetime import datetime, date, timedelta
from extensions import db
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


def seed_database():
    """Populate realistic demo records if database is empty."""
    if User.query.first():
        print("Database already contains records. Skipping seed.")
        return

    print("Seeding initial demo data for CampusConnect...")

    # 1. Departments
    dept_cs = Department(code='CSE', name='Computer Science & Engineering', description='Department of Computer Science & Software Engineering')
    dept_it = Department(code='IT', name='Information Technology', description='Department of Information Technology & Cybersecurity')
    dept_ece = Department(code='ECE', name='Electronics & Communication', description='Department of Electronics, IoT & Embedded Systems')
    dept_me = Department(code='ME', name='Mechanical Engineering', description='Department of Mechanical & Robotics Engineering')

    db.session.add_all([dept_cs, dept_it, dept_ece, dept_me])
    db.session.flush()

    # 2. Courses
    course_btech_cs = Course(code='BTECH-CSE', name='B.Tech Computer Science & Engineering', department_id=dept_cs.id, total_semesters=8, credits=160)
    course_btech_it = Course(code='BTECH-IT', name='B.Tech Information Technology', department_id=dept_it.id, total_semesters=8, credits=160)
    db.session.add_all([course_btech_cs, course_btech_it])
    db.session.flush()

    # 3. Users (Demo Roles)
    # Admin
    admin_user = User(
        full_name='Dr. Eleanor Vance',
        email='admin@campusconnect.com',
        role='admin',
        identifier='ADM-001',
        department_id=dept_cs.id,
        phone='+1 (555) 019-2831',
        bio='Campus Academic Director & System Administrator'
    )
    admin_user.set_password('Admin123!')

    # Teacher
    teacher_user = User(
        full_name='Prof. Marcus Thorne',
        email='teacher@campusconnect.com',
        role='teacher',
        identifier='FAC-102',
        department_id=dept_cs.id,
        phone='+1 (555) 019-8822',
        bio='Associate Professor of Computer Science | Specializing in Algorithms & Cloud Systems'
    )
    teacher_user.set_password('Teacher123!')

    teacher_user2 = User(
        full_name='Dr. Sophia Martinez',
        email='sophia.martinez@campusconnect.com',
        role='teacher',
        identifier='FAC-105',
        department_id=dept_cs.id,
        phone='+1 (555) 019-4411',
        bio='Senior Lecturer in Database Systems & Artificial Intelligence'
    )
    teacher_user2.set_password('Teacher123!')

    # Student (Primary Demo)
    student_user = User(
        full_name='Alex Rivers',
        email='student@campusconnect.com',
        role='student',
        identifier='STU-2025-084',
        department_id=dept_cs.id,
        semester=4,
        phone='+1 (555) 019-7734',
        bio='Computer Science sophomore passionate about Full-Stack Systems & AI'
    )
    student_user.set_password('Student123!')

    # Additional Students
    student_priya = User(
        full_name='Priya Sharma',
        email='priya.sharma@campusconnect.com',
        role='student',
        identifier='STU-2025-085',
        department_id=dept_cs.id,
        semester=4,
        phone='+1 (555) 019-3321'
    )
    student_priya.set_password('Student123!')

    student_liam = User(
        full_name='Liam Chen',
        email='liam.chen@campusconnect.com',
        role='student',
        identifier='STU-2025-086',
        department_id=dept_cs.id,
        semester=4,
        phone='+1 (555) 019-5567'
    )
    student_liam.set_password('Student123!')

    student_maya = User(
        full_name='Maya Patel',
        email='maya.patel@campusconnect.com',
        role='student',
        identifier='STU-2025-087',
        department_id=dept_cs.id,
        semester=4,
        phone='+1 (555) 019-9941'
    )
    student_maya.set_password('Student123!')

    # Club Coordinator
    coordinator_user = User(
        full_name='Sarah Jenkins',
        email='coordinator@campusconnect.com',
        role='coordinator',
        identifier='CRD-305',
        department_id=dept_cs.id,
        phone='+1 (555) 019-6612',
        bio='Lead Student Activities Coordinator & Developer Club Mentor'
    )
    coordinator_user.set_password('Coordinator123!')

    db.session.add_all([
        admin_user, teacher_user, teacher_user2,
        student_user, student_priya, student_liam, student_maya,
        coordinator_user
    ])
    db.session.flush()

    # 4. Subjects
    subj_dsa = Subject(code='CS-401', name='Data Structures & Algorithms', department_id=dept_cs.id, semester=4, credits=4, description='Core algorithmic patterns, trees, graphs, and dynamic programming.')
    subj_dbms = Subject(code='CS-402', name='Database Management Systems', department_id=dept_cs.id, semester=4, credits=4, description='Relational database architecture, SQL, ACID properties, and indexing.')
    subj_os = Subject(code='CS-403', name='Operating Systems & Concurrency', department_id=dept_cs.id, semester=4, credits=4, description='Processes, threads, virtualization, memory management, and file systems.')
    subj_cn = Subject(code='CS-404', name='Computer Networks & Protocols', department_id=dept_cs.id, semester=4, credits=3, description='TCP/IP stack, routing algorithms, socket programming, and network security.')
    subj_se = Subject(code='CS-405', name='Software Engineering & Agile', department_id=dept_cs.id, semester=4, credits=3, description='Software development lifecycles, Scrum, testing methodologies, and CI/CD.')

    db.session.add_all([subj_dsa, subj_dbms, subj_os, subj_cn, subj_se])
    db.session.flush()

    # 5. Class Rooms
    class_4a = ClassRoom(
        name='CSE-4A',
        code='CSE-SEM4-SEC-A',
        department_id=dept_cs.id,
        semester=4,
        section='A',
        academic_year='2025-2026',
        teacher_id=teacher_user.id
    )
    class_4b = ClassRoom(
        name='CSE-4B',
        code='CSE-SEM4-SEC-B',
        department_id=dept_cs.id,
        semester=4,
        section='B',
        academic_year='2025-2026',
        teacher_id=teacher_user2.id
    )
    db.session.add_all([class_4a, class_4b])
    db.session.flush()

    # 6. Enroll Students into CSE-4A
    for s in [student_user, student_priya, student_liam, student_maya]:
        cs_entry = ClassStudent(class_id=class_4a.id, student_id=s.id, roll_number=s.identifier)
        db.session.add(cs_entry)
    db.session.flush()

    # 7. Class Timetable Schedules
    schedules = [
        ClassSchedule(class_id=class_4a.id, subject_id=subj_dsa.id, teacher_id=teacher_user.id, day_of_week='Monday', start_time='09:00', end_time='10:00', room_number='LH-201'),
        ClassSchedule(class_id=class_4a.id, subject_id=subj_dbms.id, teacher_id=teacher_user2.id, day_of_week='Monday', start_time='10:15', end_time='11:15', room_number='LH-201'),
        ClassSchedule(class_id=class_4a.id, subject_id=subj_os.id, teacher_id=teacher_user.id, day_of_week='Monday', start_time='11:30', end_time='12:30', room_number='Lab-3'),
        
        ClassSchedule(class_id=class_4a.id, subject_id=subj_cn.id, teacher_id=teacher_user2.id, day_of_week='Tuesday', start_time='09:00', end_time='10:00', room_number='LH-201'),
        ClassSchedule(class_id=class_4a.id, subject_id=subj_se.id, teacher_id=teacher_user.id, day_of_week='Tuesday', start_time='10:15', end_time='11:15', room_number='LH-201'),
        ClassSchedule(class_id=class_4a.id, subject_id=subj_dsa.id, teacher_id=teacher_user.id, day_of_week='Tuesday', start_time='13:30', end_time='15:30', room_number='Lab-1'),

        ClassSchedule(class_id=class_4a.id, subject_id=subj_dsa.id, teacher_id=teacher_user.id, day_of_week='Wednesday', start_time='09:00', end_time='10:00', room_number='LH-201'),
        ClassSchedule(class_id=class_4a.id, subject_id=subj_dbms.id, teacher_id=teacher_user2.id, day_of_week='Wednesday', start_time='10:15', end_time='11:15', room_number='LH-201'),
        ClassSchedule(class_id=class_4a.id, subject_id=subj_os.id, teacher_id=teacher_user.id, day_of_week='Wednesday', start_time='11:30', end_time='12:30', room_number='LH-201'),

        ClassSchedule(class_id=class_4a.id, subject_id=subj_cn.id, teacher_id=teacher_user2.id, day_of_week='Thursday', start_time='09:00', end_time='10:00', room_number='LH-201'),
        ClassSchedule(class_id=class_4a.id, subject_id=subj_se.id, teacher_id=teacher_user.id, day_of_week='Thursday', start_time='10:15', end_time='11:15', room_number='LH-201'),

        ClassSchedule(class_id=class_4a.id, subject_id=subj_dsa.id, teacher_id=teacher_user.id, day_of_week='Friday', start_time='09:00', end_time='10:00', room_number='LH-201'),
        ClassSchedule(class_id=class_4a.id, subject_id=subj_dbms.id, teacher_id=teacher_user2.id, day_of_week='Friday', start_time='10:15', end_time='11:15', room_number='Lab-2'),
    ]
    db.session.add_all(schedules)
    db.session.flush()

    # 8. Attendance Records (Last 14 days)
    today = date.today()
    for day_offset in range(1, 15):
        att_day = today - timedelta(days=day_offset)
        if att_day.weekday() >= 5:  # Skip weekends
            continue

        for s in [student_user, student_priya, student_liam, student_maya]:
            for sub in [subj_dsa, subj_dbms, subj_os, subj_cn]:
                # Realistic distribution: mostly present, occasional absent or late
                status = 'Present'
                if s.id == student_user.id and sub.id == subj_cn.id and day_offset in [3, 7, 10]:
                    status = 'Absent'
                elif s.id == student_priya.id and day_offset in [4, 8]:
                    status = 'Absent'
                elif day_offset == 2:
                    status = 'Late'

                att_rec = Attendance(
                    student_id=s.id,
                    class_id=class_4a.id,
                    subject_id=sub.id,
                    date=att_day,
                    status=status,
                    marked_by_id=teacher_user.id
                )
                db.session.add(att_rec)
    db.session.flush()

    # 9. Results (Semester 3 & Midterm 4)
    # Semester 3 Results for Alex
    res_s3_1 = Result(student_id=student_user.id, subject_id=subj_dsa.id, class_id=class_4a.id, semester=3, internal_marks=28, assignment_marks=20, exam_marks=44, total_marks=92, max_marks=100, grade='A+', gpa_points=10.0, remarks='Outstanding analytical skills', teacher_id=teacher_user.id)
    res_s3_2 = Result(student_id=student_user.id, subject_id=subj_dbms.id, class_id=class_4a.id, semester=3, internal_marks=26, assignment_marks=19, exam_marks=41, total_marks=86, max_marks=100, grade='A', gpa_points=9.0, remarks='Solid database normalization work', teacher_id=teacher_user2.id)
    res_s3_3 = Result(student_id=student_user.id, subject_id=subj_os.id, class_id=class_4a.id, semester=3, internal_marks=24, assignment_marks=18, exam_marks=36, total_marks=78, max_marks=100, grade='B+', gpa_points=8.0, remarks='Good understanding of concurrency concepts', teacher_id=teacher_user.id)
    res_s3_4 = Result(student_id=student_user.id, subject_id=subj_cn.id, class_id=class_4a.id, semester=3, internal_marks=25, assignment_marks=19, exam_marks=40, total_marks=84, max_marks=100, grade='A', gpa_points=9.0, remarks='Well performed in network socket lab', teacher_id=teacher_user2.id)

    # Results for Priya
    res_p1 = Result(student_id=student_priya.id, subject_id=subj_dsa.id, class_id=class_4a.id, semester=3, internal_marks=29, assignment_marks=20, exam_marks=46, total_marks=95, max_marks=100, grade='A+', gpa_points=10.0, teacher_id=teacher_user.id)
    res_p2 = Result(student_id=student_priya.id, subject_id=subj_dbms.id, class_id=class_4a.id, semester=3, internal_marks=27, assignment_marks=19, exam_marks=42, total_marks=88, max_marks=100, grade='A', gpa_points=9.0, teacher_id=teacher_user2.id)

    db.session.add_all([res_s3_1, res_s3_2, res_s3_3, res_s3_4, res_p1, res_p2])
    db.session.flush()

    # 10. Announcements
    ann1 = Announcement(
        title='Mid-Semester Examination Schedule Announced',
        content='The Mid-Semester examinations for all 4th and 6th semester students will commence from March 15th, 2026. Detailed seating charts and subject timetables are available in the academic portal.',
        category='Examination',
        priority='Urgent',
        target_role='All',
        author_id=admin_user.id,
        is_pinned=True
    )
    ann2 = Announcement(
        title='CampusHack 2026: 36-Hour Hackathon Registrations Open',
        content='Calling all programmers, designers, and innovators! Annual 36-hour hackathon with cash prizes over $10,000. Register your team before Friday.',
        category='Event',
        priority='High',
        target_role='Students',
        author_id=coordinator_user.id,
        is_pinned=True
    )
    ann3 = Announcement(
        title='Library Extended Hours During Finals Week',
        content='The Central University Library will remain open 24/7 starting next Monday to assist students with exam preparation and group study sessions.',
        category='Academic',
        priority='Medium',
        target_role='All',
        author_id=admin_user.id
    )
    ann4 = Announcement(
        title='Faculty Curriculum Review Meeting',
        content='All department faculty members are requested to attend the semester syllabus and lab equipment review meeting in Conference Hall B on Friday at 3:30 PM.',
        category='General',
        priority='Medium',
        target_role='Teachers',
        author_id=admin_user.id
    )

    db.session.add_all([ann1, ann2, ann3, ann4])
    db.session.flush()

    # 11. Assignments
    asg1 = Assignment(
        title='Assignment 3: Graph Traversal & Dijkstra Implementation',
        description='Implement Dijkstra’s shortest path algorithm and A* search in Python or C++. Include unit test cases for weighted directed graphs and time complexity breakdown.',
        class_id=class_4a.id,
        subject_id=subj_dsa.id,
        teacher_id=teacher_user.id,
        max_marks=50.0,
        due_date=datetime.utcnow() + timedelta(days=4, hours=6)
    )
    asg2 = Assignment(
        title='Project Lab: Database Schema Design & B+ Tree Indexing',
        description='Design an E-Commerce relational schema conforming to 3NF. Write complex queries utilizing window functions, CTEs, and evaluate query execution plans with EXPLAIN ANALYZE.',
        class_id=class_4a.id,
        subject_id=subj_dbms.id,
        teacher_id=teacher_user2.id,
        max_marks=100.0,
        due_date=datetime.utcnow() + timedelta(days=9)
    )
    asg3 = Assignment(
        title='Lab 2: Multi-threaded Producer-Consumer Synchronization',
        description='Build a thread-safe circular buffer in C/POSIX Threads using mutex locks and condition variables to demonstrate deadlock-free concurrency.',
        class_id=class_4a.id,
        subject_id=subj_os.id,
        teacher_id=teacher_user.id,
        max_marks=30.0,
        due_date=datetime.utcnow() - timedelta(days=2)  # Past assignment
    )

    db.session.add_all([asg1, asg2, asg3])
    db.session.flush()

    # Submissions for past assignment
    sub_alex = AssignmentSubmission(
        assignment_id=asg3.id,
        student_id=student_user.id,
        submission_text='Implemented circular queue synchronization with pthread_mutex_t and pthread_cond_t. Tested with 8 producer and 8 consumer threads without race conditions.',
        status='Graded',
        marks_obtained=29.0,
        feedback='Flawless implementation and clean concurrency handling!'
    )
    sub_priya = AssignmentSubmission(
        assignment_id=asg3.id,
        student_id=student_priya.id,
        submission_text='Complete implementation with valgrind memory leak verification.',
        status='Graded',
        marks_obtained=30.0,
        feedback='Exemplary code quality and documentation.'
    )
    db.session.add_all([sub_alex, sub_priya])
    db.session.flush()

    # 12. Campus Events
    ev1 = CampusEvent(
        title='Annual Tech Innovation Summit 2026',
        description='Keynote sessions from tech industry pioneers, AI demonstrations, and campus startup pitch competition with angel investors.',
        category='Workshop',
        event_date=today + timedelta(days=6),
        start_time='10:00 AM',
        end_time='04:30 PM',
        location='Main University Auditorium',
        organizing_body='CSE Dept & Student Affairs',
        organizer_id=admin_user.id,
        max_participants=250
    )
    ev2 = CampusEvent(
        title='CampusHack 2026: 36-Hour Hackathon',
        description='36-hour sprint to build innovative hardware and software solutions tackling sustainability, healthcare, and education.',
        category='Competition',
        event_date=today + timedelta(days=12),
        start_time='09:00 AM',
        end_time='09:00 PM',
        location='Innovation Center Hall',
        organizing_body='Coding & AI Society',
        organizer_id=coordinator_user.id,
        max_participants=120
    )
    ev3 = CampusEvent(
        title='Spring Cultural Night & Talent Showcase',
        description='Annual cultural evening with live musical performances, drama club theatrics, dance exhibitions, and campus food stalls.',
        category='Cultural',
        event_date=today + timedelta(days=18),
        start_time='06:00 PM',
        end_time='10:00 PM',
        location='Open Air Amphitheatre',
        organizing_body='Cultural Club',
        organizer_id=coordinator_user.id,
        max_participants=500
    )

    db.session.add_all([ev1, ev2, ev3])
    db.session.flush()

    # Register Alex for Tech Summit
    reg_alex = EventRegistration(event_id=ev1.id, user_id=student_user.id, status='Registered')
    db.session.add(reg_alex)
    db.session.flush()

    # 13. Academic Projects
    proj1 = AcademicProject(
        title='Smart Campus IoT Energy & HVAC Optimization',
        description='An automated micro-controller based sensor network monitoring ambient temperature and occupancy to dynamically modulate HVAC energy load, reducing campus power consumption by 24%.',
        category='IoT',
        creator_id=student_user.id,
        guide_id=teacher_user.id,
        deadline=today + timedelta(days=45),
        status='In Progress',
        progress_percentage=65,
        repository_url='https://github.com/campusconnect/smart-iot-energy'
    )
    proj2 = AcademicProject(
        title='AI-Powered Automated Grading & Code Evaluation Engine',
        description='An intelligent static analysis and dynamic unit-testing sandbox for evaluating algorithmic coursework with automated AST syntax checking and plagiarism detection.',
        category='Machine Learning',
        creator_id=student_priya.id,
        guide_id=teacher_user.id,
        deadline=today + timedelta(days=60),
        status='Planning',
        progress_percentage=30,
        repository_url='https://github.com/campusconnect/ai-grader'
    )
    db.session.add_all([proj1, proj2])
    db.session.flush()

    # Project members
    db.session.add_all([
        ProjectMember(project_id=proj1.id, student_id=student_user.id, role_in_project='Team Lead & Firmware Developer'),
        ProjectMember(project_id=proj1.id, student_id=student_liam.id, role_in_project='Cloud Backend Engineer'),
        ProjectMember(project_id=proj2.id, student_id=student_priya.id, role_in_project='ML Architect')
    ])
    db.session.flush()

    # 14. Clubs
    club_code = Club(
        name='Coding & AI Society',
        code='CLUB-CODE-AI',
        description='The premier coding society hosting weekly algorithmic contests, open-source workshops, hackathons, and guest tech talks.',
        category='Technical',
        coordinator_id=coordinator_user.id,
        meeting_schedule='Every Friday at 4:30 PM in Computer Lab 3',
        website_url='https://github.com/campusconnect-club'
    )
    club_robotics = Club(
        name='Robotics & Hardware Chapter',
        code='CLUB-ROBOTICS',
        description='Designing autonomous ground vehicles, drone avionics, embedded IoT hardware, and participating in national Robocon competitions.',
        category='Innovation',
        coordinator_id=coordinator_user.id,
        meeting_schedule='Every Wednesday at 5:00 PM in Maker Space'
    )
    club_cultural = Club(
        name='Arts & Cultural Society',
        code='CLUB-CULTURE',
        description='Campus collective celebrating theater, acoustic music, classical and contemporary dance, and visual art installations.',
        category='Cultural',
        coordinator_id=coordinator_user.id,
        meeting_schedule='Every Thursday at 5:30 PM in Amphitheatre'
    )
    club_sports = Club(
        name='Campus Sports & Athletics Guild',
        code='CLUB-SPORTS',
        description='Organizing inter-department football, basketball, badminton tournaments, and fitness training sessions.',
        category='Sports',
        coordinator_id=coordinator_user.id,
        meeting_schedule='Every Saturday at 7:00 AM at University Grounds'
    )

    db.session.add_all([club_code, club_robotics, club_cultural, club_sports])
    db.session.flush()

    # Memberships
    db.session.add_all([
        ClubMember(club_id=club_code.id, student_id=student_user.id, role='Secretary', status='Active'),
        ClubMember(club_id=club_code.id, student_id=student_priya.id, role='Leader', status='Active'),
        ClubMember(club_id=club_robotics.id, student_id=student_liam.id, role='Lead Engineer', status='Active'),
        ClubMember(club_id=club_sports.id, student_id=student_user.id, role='Member', status='Active')
    ])
    db.session.flush()

    # Club activities
    act1 = ClubActivity(
        club_id=club_code.id,
        title='Weekly CodeSprint #14: Dynamic Programming & Trees',
        description='Hands-on contest solving 4 medium-hard DP problems with peer walkthroughs and pizza.',
        activity_date=datetime.now() + timedelta(days=2, hours=4),
        location='Computer Lab 3',
        points=15
    )
    act2 = ClubActivity(
        club_id=club_robotics.id,
        title='Arduino & ROS2 Autonomous Navigation Workshop',
        description='Learn sensor fusion with LiDAR and IMU using Robot Operating System 2.',
        activity_date=datetime.now() + timedelta(days=5, hours=3),
        location='Maker Space Room 102',
        points=25
    )
    db.session.add_all([act1, act2])
    db.session.flush()

    # 15. Notifications for Alex
    n1 = Notification(
        user_id=student_user.id,
        title='Assignment 3 Published',
        message='Prof. Thorne published Assignment 3 (Dijkstra Traversal) due in 4 days.',
        category='assignment',
        link_url=f'/assignments/{asg1.id}'
    )
    n2 = Notification(
        user_id=student_user.id,
        title='Event Registration Confirmed',
        message='You are successfully registered for Annual Tech Innovation Summit 2026.',
        category='event',
        link_url=f'/events/{ev1.id}'
    )
    n3 = Notification(
        user_id=student_user.id,
        title='Grade Published',
        message='Your grade for Operating Systems (Sem 3) was awarded: Grade B+ (78/100).',
        category='result',
        link_url='/results'
    )
    db.session.add_all([n1, n2, n3])

    db.session.commit()
    print("Database seeding completed successfully! Demo accounts ready.")
