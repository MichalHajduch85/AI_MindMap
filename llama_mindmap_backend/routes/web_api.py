"""Simplified web API routes for public access."""

import logging
from flask import Blueprint, request, jsonify
from llama_mindmap_backend.utils.llama_api import (
    expand_topic, breakdown_topic, analyze_topic, 
    test_api_connection, get_api_stats
)


logger = logging.getLogger(__name__)
web_api_bp = Blueprint('web_api', __name__)


def validate_topic(topic: str) -> tuple[bool, str]:
    """Validate topic input."""
    if not topic or not topic.strip():
        return False, "Topic is required"
    
    inappropriate_keywords = ['kill', 'murder', 'harm', 'violence', 'illegal', 'criminal']
    if any(keyword in topic.lower() for keyword in inappropriate_keywords):
        return False, "Inappropriate topic detected"
    
    if len(topic) > 500:
        return False, "Topic too long (max 500 characters)"
    
    return True, ""


@web_api_bp.route('/expand', methods=['POST'])
def expand_topic_endpoint():
    """Expand a topic into subtopics."""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        is_valid, error_msg = validate_topic(topic)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        logger.info(f"Expanding topic: {topic}")
        subtopics = expand_topic(topic)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'subtopics': subtopics
        })
        
    except Exception as e:
        logger.error(f"Error expanding topic: {e}")
        return jsonify({'error': str(e)}), 500


@web_api_bp.route('/breakdown', methods=['POST'])
def breakdown_topic_endpoint():
    """Break down a topic into steps."""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        is_valid, error_msg = validate_topic(topic)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        logger.info(f"Breaking down topic: {topic}")
        steps = breakdown_topic(topic)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'steps': steps
        })
        
    except Exception as e:
        logger.error(f"Error breaking down topic: {e}")
        return jsonify({'error': str(e)}), 500


@web_api_bp.route('/analyze', methods=['POST'])
def analyze_topic_endpoint():
    """Analyze a topic."""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        is_valid, error_msg = validate_topic(topic)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        logger.info(f"Analyzing topic: {topic}")
        analysis = analyze_topic(topic)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing topic: {e}")
        return jsonify({'error': str(e)}), 500


@web_api_bp.route('/test', methods=['GET'])
def test_api_endpoint():
    """Test API connection."""
    try:
        is_connected = test_api_connection()
        
        return jsonify({
            'success': True,
            'connected': is_connected,
            'message': 'API connection successful' if is_connected else 'API connection failed'
        })
        
    except Exception as e:
        logger.error(f"Error testing API: {e}")
        return jsonify({'error': str(e)}), 500


@web_api_bp.route('/status', methods=['GET'])
def api_status():
    """Get API status and statistics."""
    try:
        stats = get_api_stats()
        is_connected = test_api_connection()
        
        return jsonify({
            'success': True,
            'connected': is_connected,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        return jsonify({'error': str(e)}), 500