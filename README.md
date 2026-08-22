# CampusConnect - Student Academic Management System

![CampusConnect Banner](https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1200&auto=format&fit=crop)

**CampusConnect** is a centralized, role-based **Student Academic Management System** built with **Python 3, Flask, Bootstrap 5, SQLite, and SQLAlchemy**. Designed for universities and colleges, it streamlines academic operations, attendance tracking, coursework submissions, examination grading, project proposals, campus event management, and extracurricular club coordination.

---

## 🌟 Key Features & Modules

### 1. 👥 Role-Based Portals & Authentication
- **4 Distinct User Roles**:
  - 🎓 **Student**: Attendance reports, GPA/CGPA scorecards, assignment submissions, project repository, club memberships, event registrations.
  - 👨‍🏫 **Teacher / Faculty**: Subject classes, attendance marking, coursework assignment creation, grading portal, project mentoring.
  - 🛠️ **Administrator**: Department & semester setups, class sections, master user accounts, campus-wide announcements.
  - 🤝 **Club Coordinator**: Student society registrations, meetup schedules, activity point management.
- **Secure Authentication**: Werkzeug password hashing, session management via Flask-Login, CSRF protection with Flask-WTF.

### 2. 📊 Attendance Tracker & Automated Warning Engine
- Session-wise attendance marking (Present / Absent / Late) for classes.
- Real-time percentage calculation with subject breakdown.
- Visual warning badges when attendance falls below the mandatory **75% threshold**.

### 3. 🎓 Examination Results & CGPA Calculator
- Multi-component evaluation: Internal Assessments (30 pts), Assignments (20 pts), and Semester Exams (50 pts).
- Automated grade mapping (A+, A, B+, B, C, P, F) and 10.0 scale GPA calculation.
- Cumulative CGPA reports and printable academic transcripts.

### 4. 📝 Coursework & Assignment Submissions
- Faculty assignment creator with deadlines, attachments, and max scores.
- Student submission portal (text responses + file uploads).
- Dedicated faculty grading workflow with feedback comments and score recording.

### 5. 🚀 Academic Projects & Capstone Repository
- Student project proposal submission with technology categories (AI/ML, IoT, Web, Cybersecurity, etc.).
- Faculty mentor assignment and team member invitations.
- Live progress bars, milestone updater, GitHub repository links, and faculty evaluation notes.

### 6. 🎪 Campus Events & Summit Management
- Event listings for technical symposiums, hackathons, and cultural fests.
- Real-time attendee counter and student RSVP / registration system.

### 7. 🤝 Student Clubs & Extracurricular Societies
- Directory of technical and cultural student chapters.
- Membership join/leave workflows, scheduled meetups, and activity points tracking.

### 8. 🤖 CampusBot — Intelligent Academic Assistant
- Persistent floating assistant accessible across all pages.
- Database-aware NLP query processing: answers student questions regarding their attendance, approaching assignment deadlines, exam grades, timetable, and campus events.
- Modular architecture with clean extension points for Gemini AI integration.

---

## 🔑 Demo Login Credentials

For testing and evaluation, pre-seeded accounts are provided:

| Role | Email | Password | Identifier / Roll No |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@campus.edu` | `Admin123!` | `ADM-001` |
| **Teacher (Faculty)** | `sarah.faculty@campus.edu` | `Teacher123!` | `FAC-101` |
| **Student** | `alex.student@campus.edu` | `Student123!` | `2024-CSE-042` |
| **Student** | `priya.student@campus.edu` | `Student123!` | `2024-CSE-088` |
| **Club Coordinator** | `marcus.coord@campus.edu` | `Coord123!` | `FAC-105` |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Flask 3.0+
- **Database & ORM**: SQLite (development/production fallback) & Flask-SQLAlchemy
- **Authentication**: Flask-Login, Werkzeug Security
- **Frontend**: HTML5, Bootstrap 5.3, Bootstrap Icons, Vanilla JavaScript
- **Forms & CSRF**: Flask-WTF, WTForms
- **Environment Management**: python-dotenv
- **WSGI Production Server**: Gunicorn

---

## 📁 Directory Structure

```text
CampusConnect/
├── app/
│   ├── __init__.py            # Flask Application Factory (create_app)
│   ├── models/                # SQLAlchemy Database Models
│   │   ├── user.py            # User authentication & profile model
│   │   ├── academic.py        # Department, Subject, ClassRoom, ClassSchedule
│   │   ├── attendance.py      # Attendance records & status
│   │   ├── assignment.py      # Assignment & AssignmentSubmission
│   │   ├── result.py          # Results, Marks, and GPA calculations
│   │   ├── project.py         # Academic project proposals & team members
│   │   ├── event.py           # Campus events & event registrations
│   │   ├── club.py            # Student clubs, memberships & activities
│   │   ├── announcement.py    # Campus broadcast announcements
│   │   ├── notification.py    # System notifications
│   │   └── chatbot.py         # CampusBot query logs
│   ├── routes/                # Blueprint Controllers
│   │   ├── auth.py            # Login, registration, profile, logout
│   │   ├── dashboard.py       # Role-based dashboard routers
│   │   ├── attendance.py      # Attendance tracker & marking routes
│   │   ├── results.py         # Grade entry & student scorecard
│   │   ├── classes.py         # Classes, student rosters & timetables
│   │   ├── assignments.py     # Coursework creation, submit & grade
│   │   ├── events.py          # Events calendar & registration
│   │   ├── projects.py        # Project repository & progress updater
│   │   ├── clubs.py           # Clubs directory, join/leave, activities
│   │   ├── announcements.py   # Campus announcements
│   │   ├── notifications.py   # Notifications center
│   │   ├── chatbot.py         # Chatbot query routes
│   │   └── api.py             # REST API endpoints (/api/*)
│   ├── services/              # Business Logic & NLP Processing
│   │   ├── attendance_service.py # Attendance summary & calculations
│   │   ├── result_service.py     # CGPA/GPA & scorecard math
│   │   └── chatbot_service.py    # Database-aware query resolution engine
│   ├── static/                # Static Assets
│   │   ├── css/style.css      # Custom UI theme styling
│   │   └── js/
│   │       ├── main.js        # UI interactions & notification counters
│   │       └── chatbot.js     # CampusBot frontend client
│   └── templates/             # Jinja2 HTML Templates
│       ├── base.html          # Global layout template
│       ├── auth/              # Authentication templates
│       ├── dashboard/         # Role-specific dashboards
│       ├── attendance/        # Attendance views
│       ├── results/           # Gradebook & scorecards
│       ├── classes/           # Class rosters & timetables
│       ├── assignments/       # Assignment submission & review
│       ├── events/            # Events listing & detail
│       ├── projects/          # Projects repository & tracker
│       ├── clubs/             # Societies & meetup activities
│       ├── announcements/     # Campus broadcasts
│       ├── notifications/     # Notification center
│       ├── chatbot/           # Dedicated CampusBot page
│       └── errors/            # 403, 404, 500 error pages
├── tests/                     # Automated Test Suite (Unittest)
│   ├── test_auth.py
│   ├── test_attendance.py
│   ├── test_results.py
│   ├── test_chatbot.py
│   └── test_api.py
├── instance/                  # SQLite Database Storage (campusconnect.db)
├── app.py                     # Standalone Python entry point
├── config.py                  # Application configuration classes
├── extensions.py              # Flask extensions (db, login_manager, csrf)
├── seed_data.py               # Demo database seeder
├── requirements.txt           # Python dependencies
├── Procfile                   # Deployment entry point for Render
├── runtime.txt                # Python runtime specification
└── README.md                  # Project documentation
```

---

## 🚀 Quickstart Guide (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/CampusConnect.git
cd CampusConnect
```

### 2. Create and activate a Python virtual environment
```bash
# On macOS / Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install requirements
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (Optional)
Copy `.env.example` to `.env`:
```bash
SECRET_KEY="your-super-secret-flask-key"
FLASK_ENV="development"
MIN_ATTENDANCE_PERCENTAGE=75.0
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to **`http://localhost:5000`**. The SQLite database `instance/campusconnect.db` will be initialized and pre-seeded automatically on first startup!

---

## 🧪 Running Automated Tests

Run the test suite using Python's built-in `unittest` runner:
```bash
python -m unittest discover tests
```

All unit tests for authentication, attendance math, GPA calculation, chatbot intent parsing, and REST endpoints will execute and validate application logic.

---

## 🌐 Deploying to Render

CampusConnect is pre-configured for one-click deployment on **Render**:

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - CampusConnect Academic Management System"
   git branch -M main
   git remote add origin https://github.com/your-username/campusconnect.git
   git push -u origin main
   ```
2. **Create a New Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/) -> **New** -> **Web Service**.
   - Connect your GitHub repository.
   - Set **Runtime**: `Python 3`.
   - Set **Build Command**: `pip install -r requirements.txt`.
   - Set **Start Command**: `gunicorn "app:create_app()"` (or rely on `Procfile`).
3. **Set Environment Variables**:
   - `SECRET_KEY`: (A random secure string)
   - `FLASK_ENV`: `production`
   - `PYTHON_VERSION`: `3.10.12`
4. Click **Deploy Web Service**.

---

## 📄 License & Credits

Developed with ❤️ for universities and academic institutions. Built using Flask, Bootstrap, SQLAlchemy, and Python.
