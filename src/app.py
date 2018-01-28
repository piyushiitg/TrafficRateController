#!flask/bin/python

from flask import Flask
from functools import wraps
import redis_helper
import rate_limit
from flask import request
import json
#from flask.ext.api import status
from flask_api import status

app = Flask(__name__)
redis_manager = None

def load_configuration():
    global redis_manager
    with open("../config/rate_limit.json") as fp:
        json_obj = json.load(fp)

    # Update the config json to redis for later access
    redis_manager.set_key("rate_limit", json_obj)

def create_redis_manager():
    redis_manager = redis_helper.RedisManager(host='localhost', port=6379)
    return redis_manager

def delete_data_from_redis():
    global redis_manager
    config_json = redis_manager.get_config_json()
    client_id = config_json.get("client")
    # Delete existing keys if before stating up
    client_pattern = "%s_*" % (client_id)
    redis_manager.delete_keys(client_pattern) 

def api_rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        url = request.path
        method = request.method
        rate_limit_obj = rate_limit.RateLimiter(redis_manager.redis_conn)
        config_json = redis_manager.get_config_json()
        client_id = config_json.get("client")
        for config in config_json.get("specialization", []):
            rate_limit_type = config.get("type")
            rate_limit_name = config.get("name")
            limits = config.get("limit", {})

            if rate_limit_type == "METHOD" and rate_limit_name == method:
                if not rate_limit_obj.check_rate_limit(client_id, limits, rate_limit_name):
                    content = "Rate limit exceeded for URL %s with %s method, wait for sometime" % (url, method)
                    return content, status.HTTP_429_TOO_MANY_REQUESTS 
            elif rate_limit_type == "API" and rate_limit_name == url:
                if not rate_limit_obj.check_rate_limit(client_id, limits, rate_limit_name):
                    content = "Rate limit exceeded for API, wait for sometime. %s" % (url)
                    return content, status.HTTP_429_TOO_MANY_REQUESTS 
                
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@api_rate_limit
def index():
    return "Hello, World!", status.HTTP_200_OK

@app.route('/status')
@api_rate_limit
def api_status():
    return "Hello, Status!", status.HTTP_200_OK

@app.route('/pay')
@api_rate_limit
def pay():
    return "Hello Pay", status.HTTP_200_OK

@app.route('/check')
@api_rate_limit
def check():
    return "Hello, Check!", status.HTTP_200_OK

if __name__ == '__main__':
    try:
        redis_manager = create_redis_manager()
        load_configuration()
        delete_data_from_redis()
        app.run(debug=True)
    except Exception, err:
        print "Exception occurred while starting application", err
    finally:
        #redis_manager.close_connection()
        pass

