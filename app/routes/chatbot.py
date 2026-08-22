from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from extensions import csrf
from app.services.chatbot_service import process_student_query

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/chatbot')
@chatbot_bp.route('/chatbot/')
def chatbot_page():
    return render_template('chatbot/index.html')


@chatbot_bp.route('/api/chatbot', methods=['POST'])
@csrf.exempt
def api_chatbot():
    """
    POST /api/chatbot
    Payload: JSON { "message": "query string" } or Form Data
    Returns: JSON response with student data and suggestions
    """
    data = request.get_json(silent=True) or request.form
    message = data.get('message', '').strip()

    if not message:
        return jsonify({
            'error': 'Message content cannot be empty.',
            'response': 'Please type a question or choose one of the suggested actions.'
        }), 400

    result = process_student_query(current_user if current_user.is_authenticated else None, message)
    return jsonify(result)
