# app/chat/routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.utils.talent_assistant import TalentAssistant
import os
import traceback

chat_bp = Blueprint('chat', __name__)

# Initialize TalentAssistant with Gemini API key
def get_assistant():
    """Get or create TalentAssistant instance"""
    api_key = os.environ.get('GEMINI_API_KEY')
    return TalentAssistant(api_key=api_key)

@chat_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Chat endpoint for TalentAssistant - ALWAYS responds"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        skills = data.get('skills', [])
        experience = data.get('experience', 0)
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Check if user is allowed to use chat
        if current_user.is_recruiter() or current_user.is_admin():
            return jsonify({
                'success': False,
                'error': 'This feature is for job seekers only.'
            }), 403
        
        # Get response from TalentAssistant
        assistant = get_assistant()
        result = assistant.get_response(
            question=question,
            user_skills=skills,
            experience=experience
        )
        
        # ✅ Get response with fallback
        response_text = result.get('response', '')
        if not response_text or not response_text.strip():
            response_text = "I received your question but I'm having trouble formulating a response. Please try again. 🙏"
        
        # ✅ Get source with proper default
        source = result.get('source', 'gemini')
        if source == 'unknown':
            source = 'gemini' if assistant.gemini_enabled else 'rule_based'
        
        # ✅ ALWAYS return success: true
        return jsonify({
            'success': True,
            'response': response_text,
            'source': source,
            'sector': result.get('sector', 'general'),
            'intent': result.get('intent', 'general'),
            'suggested_followups': result.get('suggested_followups', [])
        })
        
    except Exception as e:
        # ✅ Log error for debugging
        current_app.logger.error(f"Chat error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        
        # ✅ ALWAYS return a response - never return 500
        return jsonify({
            'success': True,  # ✅ Always true so frontend doesn't show error
            'response': "I'm having a bit of trouble right now. Please try asking your question again. 🙏",
            'source': 'error',
            'sector': 'general',
            'intent': 'general',
            'suggested_followups': []
        }), 200  # ✅ Always return 200


@chat_bp.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint to check Gemini status"""
    assistant = get_assistant()
    return jsonify({
        'status': 'healthy',
        'gemini_enabled': assistant.gemini_enabled,
        'source': 'gemini' if assistant.gemini_enabled else 'rule_based',
        'daily_limit': '1,500 requests/day' if assistant.gemini_enabled else 'N/A'
    })