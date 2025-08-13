from flask import Flask, render_template, jsonify, request
import redis
import random
import string
import json
import uuid
import ssl
from datetime import datetime

app = Flask(__name__)

# Redis connection configuration for TLS-enabled database
REDIS_HOST = "mydbsecond-headless.rec-naresh.svc.cluster.local"
REDIS_PORT = 18777
REDIS_USERNAME = "default"
REDIS_PASSWORD = ""

# TLS certificate paths
CLIENT_CERT_PATH = "/app/client_cert.pem"
CLIENT_KEY_PATH = "/app/client_key.pem"
SERVER_CA_PATH = "/app/server-ca.crt"

# Initialize Redis connection with TLS
r = None
try:
    print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT} with TLS...")

    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        ssl=True,
        ssl_cert_reqs=ssl.CERT_NONE,  # Skip certificate verification for testing
        ssl_certfile=CLIENT_CERT_PATH,
        ssl_keyfile=CLIENT_KEY_PATH,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=10
    )

    # Test connection
    r.ping()
    print("Successfully connected to Redis with TLS!")

except Exception as e:
    print(f"Failed to connect to Redis: {e}")
    r = None

def generate_random_string(length=10):
    """Generate a random string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_data():
    """Generate random data for Redis operations"""
    return {
        'name': random.choice(['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry']),
        'age': random.randint(18, 80),
        'city': random.choice(['New York', 'London', 'Tokyo', 'Paris', 'Sydney', 'Mumbai', 'Berlin']),
        'score': random.randint(1, 100),
        'timestamp': datetime.now().isoformat()
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_strings', methods=['POST'])
def generate_strings():
    """Generate 10 random strings and store in Redis"""
    if not r:
        return jsonify({'error': 'Redis connection not available'}), 500
    
    try:
        results = []
        for i in range(10):
            key = f"string:{uuid.uuid4().hex[:8]}"
            value = generate_random_string(20)
            r.set(key, value)
            results.append({'key': key, 'value': value})
        
        return jsonify({'success': True, 'data': results, 'type': 'strings'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_hashes', methods=['POST'])
def generate_hashes():
    """Generate 10 random hashes and store in Redis"""
    if not r:
        return jsonify({'error': 'Redis connection not available'}), 500
    
    try:
        results = []
        for i in range(10):
            key = f"hash:{uuid.uuid4().hex[:8]}"
            data = generate_random_data()
            r.hset(key, mapping=data)
            results.append({'key': key, 'value': data})
        
        return jsonify({'success': True, 'data': results, 'type': 'hashes'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_sets', methods=['POST'])
def generate_sets():
    """Generate 10 random sets and store in Redis"""
    if not r:
        return jsonify({'error': 'Redis connection not available'}), 500
    
    try:
        results = []
        for i in range(10):
            key = f"set:{uuid.uuid4().hex[:8]}"
            members = [generate_random_string(8) for _ in range(random.randint(3, 8))]
            r.sadd(key, *members)
            results.append({'key': key, 'value': members})
        
        return jsonify({'success': True, 'data': results, 'type': 'sets'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_lists', methods=['POST'])
def generate_lists():
    """Generate 10 random lists and store in Redis"""
    if not r:
        return jsonify({'error': 'Redis connection not available'}), 500
    
    try:
        results = []
        for i in range(10):
            key = f"list:{uuid.uuid4().hex[:8]}"
            items = [generate_random_string(10) for _ in range(random.randint(3, 7))]
            r.lpush(key, *items)
            results.append({'key': key, 'value': items})
        
        return jsonify({'success': True, 'data': results, 'type': 'lists'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_sorted_sets', methods=['POST'])
def generate_sorted_sets():
    """Generate 10 random sorted sets and store in Redis"""
    if not r:
        return jsonify({'error': 'Redis connection not available'}), 500
    
    try:
        results = []
        for i in range(10):
            key = f"zset:{uuid.uuid4().hex[:8]}"
            members = {}
            for _ in range(random.randint(3, 6)):
                member = generate_random_string(8)
                score = random.randint(1, 100)
                members[member] = score
            
            r.zadd(key, members)
            results.append({'key': key, 'value': members})
        
        return jsonify({'success': True, 'data': results, 'type': 'sorted_sets'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_stats', methods=['GET'])
def get_stats():
    """Get Redis database statistics"""
    if not r:
        return jsonify({'error': 'Redis connection not available'}), 500
    
    try:
        info = r.info()
        stats = {
            'total_keys': r.dbsize(),
            'used_memory': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 'N/A'),
            'redis_version': info.get('redis_version', 'N/A'),
            'uptime_in_seconds': info.get('uptime_in_seconds', 'N/A')
        }
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_all', methods=['POST'])
def clear_all():
    """Clear all keys from the database (use with caution!)"""
    if not r:
        return jsonify({'error': 'Redis connection not available'}), 500
    
    try:
        r.flushdb()
        return jsonify({'success': True, 'message': 'All keys cleared from database'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
