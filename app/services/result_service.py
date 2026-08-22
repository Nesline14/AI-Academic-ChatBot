from collections import defaultdict
from app.models.result import Result


def get_student_academic_summary(student_id):
    """
    Calculate GPA, CGPA, total marks, percentage, and semester breakdowns for a student.
    """
    results = Result.query.filter_by(student_id=student_id).all()
    
    if not results:
        return {
            'total_subjects': 0,
            'passed_subjects': 0,
            'failed_subjects': 0,
            'cgpa': 0.0,
            'overall_percentage': 0.0,
            'semesters': {},
            'recent_results': []
        }

    total_subjects = len(results)
    passed_subjects = sum(1 for r in results if r.grade != 'F')
    failed_subjects = total_subjects - passed_subjects

    total_marks_obtained = sum(r.total_marks for r in results)
    total_max_marks = sum(r.max_marks for r in results)
    
    overall_percentage = round((total_marks_obtained / total_max_marks) * 100, 2) if total_max_marks > 0 else 0.0
    cgpa = round(sum(r.gpa_points for r in results) / total_subjects, 2) if total_subjects > 0 else 0.0

    # Semester-wise grouping
    semesters = defaultdict(list)
    for r in results:
        semesters[r.semester].append(r)

    semester_data = {}
    for sem, sem_results in sorted(semesters.items()):
        sem_total_obt = sum(r.total_marks for r in sem_results)
        sem_max = sum(r.max_marks for r in sem_results)
        sem_pct = round((sem_total_obt / sem_max) * 100, 2) if sem_max > 0 else 0.0
        sem_gpa = round(sum(r.gpa_points for r in sem_results) / len(sem_results), 2) if sem_results else 0.0

        semester_data[sem] = {
            'semester': sem,
            'results': sem_results,
            'gpa': sem_gpa,
            'percentage': sem_pct,
            'total_marks': sem_total_obt,
            'max_marks': sem_max,
            'subject_count': len(sem_results)
        }

    return {
        'total_subjects': total_subjects,
        'passed_subjects': passed_subjects,
        'failed_subjects': failed_subjects,
        'cgpa': cgpa,
        'overall_percentage': overall_percentage,
        'total_marks_obtained': total_marks_obtained,
        'total_max_marks': total_max_marks,
        'semesters': semester_data,
        'recent_results': sorted(results, key=lambda r: r.created_at, reverse=True)[:5]
    }
