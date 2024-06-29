from flask import Blueprint, jsonify, request
from .models import Query, QueryStatus
from . import mongo, redis_client

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify(message="Hello, World!")

@bp.route('/health')
def health_check():
    """Health check of the Flask Query Service"""
    response = {
        'status': 'healthy',
        'message': 'Flask Query Service is running'
    }
    return jsonify(response), 200

@bp.route('/add-search-queries', methods=['POST'])
def create_search_queries():
    if request.is_json:
        data = request.get_json()
        search_queries = data.get('search_queries', [])
        
        if not isinstance(search_queries, list):
            return jsonify({"error": "Invalid data format. 'search_queries' should be a list."}), 400
        
        response = []
        for query_string in search_queries:
            query = Query(search_string=query_string, status=QueryStatus.ADDED)
            # create redis job

            # push to mongoDB last STEP


        return jsonify(response), 201
    else:
        return jsonify({"error": "Request must be JSON"}), 400
