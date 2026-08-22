import os
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime


def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'zip'})


def save_uploaded_file(file_storage, subfolder=''):
    """Save an uploaded file safely and return the relative path."""
    if not file_storage or file_storage.filename == '':
        return None
    
    if not allowed_file(file_storage.filename):
        return None
        
    filename = secure_filename(file_storage.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(target_dir, exist_ok=True)
    
    full_path = os.path.join(target_dir, unique_filename)
    file_storage.save(full_path)
    
    if subfolder:
        return os.path.join(subfolder, unique_filename).replace('\\', '/')
    return unique_filename


def calculate_cgpa(results_list):
    """Calculate cumulative GPA on scale of 10.0 based on passed results."""
    if not results_list:
        return 0.0
    total_gpa = sum(r.gpa_points for r in results_list)
    return round(total_gpa / len(results_list), 2)
