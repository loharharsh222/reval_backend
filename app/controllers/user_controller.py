from flask import Blueprint, request, jsonify
from app.models.user import User, UserInteraction
from app import db
from datetime import datetime
from sqlalchemy import desc

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['username', 'email']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    }), 201

@user_bp.route('/users/sync-clerk', methods=['POST'])
def sync_clerk_user():
    data = request.get_json()
    
    # Validate required fields from Clerk
    if not all(k in data for k in ['clerk_id', 'username', 'email']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists with this Clerk ID
    user = User.query.filter_by(clerk_id=data['clerk_id']).first()
    
    if user:
        # Update existing user
        user.username = data['username']
        user.email = data['email']
        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        })
    
    # Create new user
    user = User(
        clerk_id=data['clerk_id'],
        username=data['username'],
        email=data['email']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    }), 201

@user_bp.route('/users/<int:user_id>/interactions', methods=['POST'])
def create_interaction(user_id):
    data = request.get_json()
    
    # Validate user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Validate required fields
    if not all(k in data for k in ['prompt', 'response']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create new interaction
    interaction = UserInteraction(
        user_id=user_id,
        prompt=data['prompt'],
        response=data['response'],
        token_overlap=data.get('token_overlap'),
        length_ratio=data.get('length_ratio'),
        relevance_score=data.get('relevance_score'),
        logical_consistency=data.get('logical_consistency'),
        math_validity=data.get('math_validity'),
        user_rating=data.get('user_rating')
    )
    
    db.session.add(interaction)
    db.session.commit()
    
    return jsonify(interaction.to_dict()), 201

@user_bp.route('/users/<int:user_id>/interactions', methods=['GET'])
def get_user_interactions(user_id):
    # Validate user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get all interactions for the user
    interactions = UserInteraction.query.filter_by(user_id=user_id).all()
    
    return jsonify([interaction.to_dict() for interaction in interactions])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat(),
        'interaction_count': len(user.interactions)
    })

@user_bp.route('/users/me', methods=['GET'])
def get_current_user():
    clerk_id = request.headers.get('X-Clerk-User-Id')
    if not clerk_id:
        return jsonify({'error': 'No Clerk user ID provided'}), 401
    
    user = User.query.filter_by(clerk_id=clerk_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat(),
        'interaction_count': len(user.interactions)
    })

@user_bp.route('/users/me/interactions', methods=['GET'])
def get_my_interactions():
    clerk_id = request.headers.get('X-Clerk-User-Id')
    if not clerk_id:
        return jsonify({'error': 'No Clerk user ID provided'}), 401
    
    user = User.query.filter_by(clerk_id=clerk_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get query parameters for pagination and sorting
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Validate sort_by parameter
    valid_sort_columns = ['created_at', 'token_overlap', 'length_ratio', 'relevance_score']
    if sort_by not in valid_sort_columns:
        sort_by = 'created_at'
    
    # Create query
    query = UserInteraction.query.filter_by(user_id=user.id)
    
    # Apply sorting
    if order == 'desc':
        query = query.order_by(desc(getattr(UserInteraction, sort_by)))
    else:
        query = query.order_by(getattr(UserInteraction, sort_by))
    
    # Apply pagination
    paginated_interactions = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'interactions': [interaction.to_dict() for interaction in paginated_interactions.items],
        'total': paginated_interactions.total,
        'pages': paginated_interactions.pages,
        'current_page': page
    })

@user_bp.route('/users/me/stats', methods=['GET'])
def get_user_stats():
    clerk_id = request.headers.get('X-Clerk-User-Id')
    if not clerk_id:
        return jsonify({'error': 'No Clerk user ID provided'}), 401
    
    user = User.query.filter_by(clerk_id=clerk_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Calculate average metrics
    interactions = UserInteraction.query.filter_by(user_id=user.id).all()
    
    if not interactions:
        return jsonify({
            'total_interactions': 0,
            'average_metrics': {
                'token_overlap': 0,
                'length_ratio': 0,
                'relevance_score': 0,
                'logical_consistency': 0,
                'math_validity': 0,
                'user_rating': 0
            }
        })
    
    total_interactions = len(interactions)
    metrics = {
        'token_overlap': sum(i.token_overlap or 0 for i in interactions) / total_interactions,
        'length_ratio': sum(i.length_ratio or 0 for i in interactions) / total_interactions,
        'relevance_score': sum(i.relevance_score or 0 for i in interactions) / total_interactions,
        'logical_consistency': sum(i.logical_consistency or 0 for i in interactions) / total_interactions,
        'math_validity': sum(i.math_validity or 0 for i in interactions) / total_interactions,
        'user_rating': sum(i.user_rating or 0 for i in interactions) / total_interactions
    }
    
    return jsonify({
        'total_interactions': total_interactions,
        'average_metrics': metrics
    })

@user_bp.route('/users/me/interactions', methods=['POST'])
def create_my_interaction():
    clerk_id = request.headers.get('X-Clerk-User-Id')
    if not clerk_id:
        return jsonify({'error': 'No Clerk user ID provided'}), 401
    
    data = request.get_json()
    
    # Validate user exists
    user = User.query.filter_by(clerk_id=clerk_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Validate required fields
    if not all(k in data for k in ['prompt', 'response']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create new interaction
    interaction = UserInteraction(
        user_id=user.id,
        prompt=data['prompt'],
        response=data['response'],
        token_overlap=data.get('token_overlap'),
        length_ratio=data.get('length_ratio'),
        relevance_score=data.get('relevance_score'),
        logical_consistency=data.get('logical_consistency'),
        math_validity=data.get('math_validity'),
        user_rating=data.get('user_rating')
    )
    
    try:
        db.session.add(interaction)
        db.session.commit()
        return jsonify(interaction.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error storing interaction: {str(e)}")
        return jsonify({'error': 'Failed to store interaction'}), 500 