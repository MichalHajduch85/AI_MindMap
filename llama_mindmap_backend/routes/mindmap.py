from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from llama_mindmap_backend.extensions import db
from llama_mindmap_backend.models import User, Conversation, Node, Log
from llama_mindmap_backend.utils.llama_api import expand_topic, breakdown_topic, analyze_topic
import uuid
from datetime import datetime

mindmap_bp = Blueprint('mindmap', __name__)

@mindmap_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """
    Get all conversations for the current user
    ---
    tags:
      - MindMap
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of conversations
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              root_topic:
                type: string
              created_at:
                type: string
              node_count:
                type: integer
    """
    user_id = get_jwt_identity()
    conversations = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.created_at.desc()).all()
    
    result = []
    for conv in conversations:
        result.append({
            'id': str(conv.id),
            'root_topic': conv.root_topic,
            'created_at': conv.created_at.isoformat(),
            'node_count': len(conv.nodes)
        })
    
    return jsonify(result), 200

@mindmap_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """
    Create a new conversation with root topic
    ---
    tags:
      - MindMap
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: conversation
        schema:
          type: object
          required:
            - root_topic
          properties:
            root_topic:
              type: string
    responses:
      201:
        description: Conversation created
        schema:
          type: object
          properties:
            id:
              type: string
            message:
              type: string
    """
    data = request.get_json()
    user_id = get_jwt_identity()
    
    if not data or 'root_topic' not in data:
        return jsonify({'message': 'Root topic is required'}), 400
    
    root_topic = data['root_topic'].strip()
    if not root_topic:
        return jsonify({'message': 'Root topic cannot be empty'}), 400
    
    # Create conversation
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=user_id,
        root_topic=root_topic
    )
    
    # Create root node
    root_node = Node(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        content=root_topic,
        level=0
    )
    
    try:
        db.session.add(conversation)
        db.session.add(root_node)
        db.session.commit()
        
        # Log the activity
        log = Log(
            user_id=user_id,
            event_type='conversation_created',
            event_data={'conversation_id': str(conversation.id), 'root_topic': root_topic}
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'id': str(conversation.id),
            'message': 'Conversation created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create conversation'}), 500

@mindmap_bp.route('/conversations/<conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """
    Get conversation with all nodes
    ---
    tags:
      - MindMap
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: conversation_id
        type: string
        required: true
    responses:
      200:
        description: Conversation with nodes
        schema:
          type: object
          properties:
            id:
              type: string
            root_topic:
              type: string
            nodes:
              type: array
              items:
                type: object
    """
    user_id = get_jwt_identity()
    
    try:
        conversation = Conversation.query.filter_by(
            id=conversation_id, 
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({'message': 'Conversation not found'}), 404
        
        nodes = Node.query.filter_by(conversation_id=conversation_id).all()
        
        def build_node_tree(nodes, parent_id=None):
            result = []
            for node in nodes:
                if node.parent_id == parent_id:
                    node_data = {
                        'id': str(node.id),
                        'content': node.content,
                        'level': node.level,
                        'steps': node.steps,
                        'analysis': node.analysis,
                        'created_at': node.created_at.isoformat(),
                        'children': build_node_tree(nodes, node.id)
                    }
                    result.append(node_data)
            return result
        
        return jsonify({
            'id': str(conversation.id),
            'root_topic': conversation.root_topic,
            'created_at': conversation.created_at.isoformat(),
            'nodes': build_node_tree(nodes)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to retrieve conversation'}), 500

@mindmap_bp.route('/nodes/<node_id>/expand', methods=['POST'])
@jwt_required()
def expand_node(node_id):
    """
    Expand a node into subtopics
    ---
    tags:
      - MindMap
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: node_id
        type: string
        required: true
    responses:
      200:
        description: Node expanded successfully
        schema:
          type: object
          properties:
            message:
              type: string
            children:
              type: array
              items:
                type: object
    """
    user_id = get_jwt_identity()
    
    try:
        # Get the node and verify ownership
        node = Node.query.join(Conversation).filter(
            Node.id == node_id,
            Conversation.user_id == user_id
        ).first()
        
        if not node:
            return jsonify({'message': 'Node not found'}), 404
        
        # Check if already expanded
        existing_children = Node.query.filter_by(parent_id=node_id).first()
        if existing_children:
            return jsonify({'message': 'Node already expanded'}), 400
        
        # Check level limit
        if node.level >= 25:
            return jsonify({'message': 'Maximum level reached'}), 400
        
        # Call LLaMA API to expand
        subtopics = expand_topic(node.content)
        
        # Create child nodes
        children = []
        for subtopic in subtopics:
            child_node = Node(
                id=uuid.uuid4(),
                conversation_id=node.conversation_id,
                parent_id=node.id,
                content=subtopic,
                level=node.level + 1
            )
            db.session.add(child_node)
            children.append({
                'id': str(child_node.id),
                'content': child_node.content,
                'level': child_node.level,
                'steps': None,
                'analysis': None,
                'children': []
            })
        
        db.session.commit()
        
        # Log the activity
        log = Log(
            user_id=user_id,
            event_type='node_expanded',
            event_data={
                'node_id': str(node.id),
                'content': node.content,
                'level': node.level,
                'subtopics_count': len(subtopics)
            }
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Node expanded successfully',
            'children': children
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error expanding node: {str(e)}")
        return jsonify({'message': 'Failed to expand node'}), 500

@mindmap_bp.route('/nodes/<node_id>/steps', methods=['POST'])
@jwt_required()
def generate_steps(node_id):
    """
    Generate steps for a node
    ---
    tags:
      - MindMap
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: node_id
        type: string
        required: true
    responses:
      200:
        description: Steps generated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            steps:
              type: array
              items:
                type: string
    """
    user_id = get_jwt_identity()
    
    try:
        # Get the node and verify ownership
        node = Node.query.join(Conversation).filter(
            Node.id == node_id,
            Conversation.user_id == user_id
        ).first()
        
        if not node:
            return jsonify({'message': 'Node not found'}), 404
        
        # Generate steps using LLaMA API
        steps = breakdown_topic(node.content)
        
        # Update node with steps
        node.steps = steps
        db.session.commit()
        
        # Log the activity
        log = Log(
            user_id=user_id,
            event_type='steps_generated',
            event_data={
                'node_id': str(node.id),
                'content': node.content,
                'steps_count': len(steps)
            }
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Steps generated successfully',
            'steps': steps
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating steps: {str(e)}")
        return jsonify({'message': 'Failed to generate steps'}), 500

@mindmap_bp.route('/nodes/<node_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_node(node_id):
    """
    Analyze a node
    ---
    tags:
      - MindMap
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: node_id
        type: string
        required: true
    responses:
      200:
        description: Analysis generated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            analysis:
              type: string
    """
    user_id = get_jwt_identity()
    
    try:
        # Get the node and verify ownership
        node = Node.query.join(Conversation).filter(
            Node.id == node_id,
            Conversation.user_id == user_id
        ).first()
        
        if not node:
            return jsonify({'message': 'Node not found'}), 404
        
        # Generate analysis using LLaMA API
        analysis = analyze_topic(node.content)
        
        # Update node with analysis
        node.analysis = analysis
        db.session.commit()
        
        # Log the activity
        log = Log(
            user_id=user_id,
            event_type='analysis_generated',
            event_data={
                'node_id': str(node.id),
                'content': node.content,
                'analysis_length': len(analysis)
            }
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis generated successfully',
            'analysis': analysis
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating analysis: {str(e)}")
        return jsonify({'message': 'Failed to generate analysis'}), 500

@mindmap_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """
    Delete a conversation and all its nodes
    ---
    tags:
      - MindMap
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: conversation_id
        type: string
        required: true
    responses:
      200:
        description: Conversation deleted successfully
    """
    user_id = get_jwt_identity()
    
    try:
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({'message': 'Conversation not found'}), 404
        
        # Delete all nodes first (due to foreign key constraints)
        Node.query.filter_by(conversation_id=conversation_id).delete()
        
        # Delete the conversation
        db.session.delete(conversation)
        db.session.commit()
        
        # Log the activity
        log = Log(
            user_id=user_id,
            event_type='conversation_deleted',
            event_data={
                'conversation_id': str(conversation_id),
                'root_topic': conversation.root_topic
            }
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Conversation deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting conversation: {str(e)}")
        return jsonify({'message': 'Failed to delete conversation'}), 500

@mindmap_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    Get user statistics
    ---
    tags:
      - MindMap
    security:
      - bearerAuth: []
    responses:
      200:
        description: User statistics
        schema:
          type: object
          properties:
            total_conversations:
              type: integer
            total_nodes:
              type: integer
            total_steps:
              type: integer
            total_analyses:
              type: integer
    """
    user_id = get_jwt_identity()
    
    try:
        # Get conversation count
        conversation_count = Conversation.query.filter_by(user_id=user_id).count()
        
        # Get node count
        node_count = Node.query.join(Conversation).filter(
            Conversation.user_id == user_id
        ).count()
        
        # Get steps count
        steps_count = Node.query.join(Conversation).filter(
            Conversation.user_id == user_id,
            Node.steps.isnot(None)
        ).count()
        
        # Get analysis count
        analysis_count = Node.query.join(Conversation).filter(
            Conversation.user_id == user_id,
            Node.analysis.isnot(None)
        ).count()
        
        return jsonify({
            'total_conversations': conversation_count,
            'total_nodes': node_count,
            'total_steps': steps_count,
            'total_analyses': analysis_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'message': 'Failed to get statistics'}), 500