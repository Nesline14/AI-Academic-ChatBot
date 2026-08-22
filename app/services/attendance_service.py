from collections import defaultdict
from app.models.attendance import Attendance
from app.models.academic import Subject, ClassRoom, ClassStudent
from flask import current_app


def get_student_attendance_summary(student_id):
    """
    Calculate comprehensive attendance metrics for a student:
    - Overall attendance percentage
    - Total classes held, attended, missed, and late
    - Subject-wise breakdown with individual percentages
    - Warning indicator if attendance falls below threshold (75%)
    """
    attendances = Attendance.query.filter_by(student_id=student_id).all()
    min_threshold = current_app.config.get('MIN_ATTENDANCE_PERCENTAGE', 75.0)

    total_classes = len(attendances)
    if total_classes == 0:
        return {
            'total_classes': 0,
            'attended': 0,
            'missed': 0,
            'late': 0,
            'overall_percentage': 100.0,
            'is_below_threshold': False,
            'min_threshold': min_threshold,
            'subjects': [],
            'history': []
        }

    attended = sum(1 for a in attendances if a.status in ['Present', 'Late'])
    present_only = sum(1 for a in attendances if a.status == 'Present')
    missed = sum(1 for a in attendances if a.status == 'Absent')
    late = sum(1 for a in attendances if a.status == 'Late')

    overall_percentage = round((attended / total_classes) * 100, 2)
    is_below_threshold = overall_percentage < min_threshold

    # Subject-wise calculation
    subject_map = defaultdict(lambda: {'total': 0, 'present': 0, 'absent': 0, 'late': 0, 'name': '', 'code': ''})
    
    for a in attendances:
        s_id = a.subject_id
        subject_map[s_id]['total'] += 1
        if a.subject:
            subject_map[s_id]['name'] = a.subject.name
            subject_map[s_id]['code'] = a.subject.code
        if a.status == 'Present':
            subject_map[s_id]['present'] += 1
        elif a.status == 'Late':
            subject_map[s_id]['late'] += 1
        else:
            subject_map[s_id]['absent'] += 1

    subject_list = []
    for s_id, stats in subject_map.items():
        sub_attended = stats['present'] + stats['late']
        sub_pct = round((sub_attended / stats['total']) * 100, 2) if stats['total'] > 0 else 0
        subject_list.append({
            'subject_id': s_id,
            'name': stats['name'] or f'Subject #{s_id}',
            'code': stats['code'] or 'N/A',
            'total': stats['total'],
            'attended': sub_attended,
            'absent': stats['absent'],
            'late': stats['late'],
            'percentage': sub_pct,
            'is_below_threshold': sub_pct < min_threshold
        })

    subject_list.sort(key=lambda x: x['name'])

    return {
        'total_classes': total_classes,
        'attended': attended,
        'present_only': present_only,
        'missed': missed,
        'late': late,
        'overall_percentage': overall_percentage,
        'is_below_threshold': is_below_threshold,
        'min_threshold': min_threshold,
        'subjects': subject_list,
        'history': sorted(attendances, key=lambda a: a.date, reverse=True)
    }
