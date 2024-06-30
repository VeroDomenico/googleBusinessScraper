from flask import Blueprint, jsonify, request
from .models import Query, QueryStatus
from . import mongo, redis_client
import datetime
from celery.result import AsyncResult
from app.workers import scrape_site

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
        print(data)
        search_queries = data.get('search_queries', [])
        
        if not isinstance(search_queries, list):
            return jsonify({"error": "Invalid data format. 'search_queries' should be a list."}), 400
        
        created_queries = []
        print(search_queries)
        for query_data in search_queries:
            search_string = query_data.get('search_string')
            if not search_string:
                return jsonify({"error": "Each query must have 'search_string'."}), 400
            print(search_string)
            query = Query(
                search_string=search_string,
                status=QueryStatus.ADDED,
                createdTime=datetime.datetime.utcnow(),
                completedTime=None,
                numberOfBusinessScraped=0
            )
            
            # Create Redis job
            # redis_task_id = redis_client.rpush('query_jobs', query.to_dict())
            # query.redis_task_id = redis_task_id
            
            # Save query to MongoDB
            db = mongo.cx.query_service
            query_id = db.queries_search.insert_one(query.to_dict()).inserted_id
            
            #Start Scrape job
            scrape_site(query.search_string)
            
            

        return jsonify(created_queries), 201
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@bp.route('/test-mongo-insert', methods=['POST'])
def test_mongo_insert():
    """
    Test route to insert a document into MongoDB
    """
    db = mongo.cx.query_service
    
    print(db.list_collection_names())
    col = db.queries_search
    res= col.insert_one({"test":"test"})
    return jsonify({"status": "success", "inserted_id": str(res.inserted_id)}), 201