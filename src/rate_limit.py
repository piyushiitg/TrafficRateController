import time
import json
import sys
import redis_helper

class RateLimiter(object):
    def __init__(self, redis_conn):
        self.interval_dict = {
                              "SEC": 1,
                              "MIN": 60,
                              "HOUR": 60 * 60,
                              "WEEK": 7*24*3600,
                              "MONTH": 30*24*3600
                             }
        self.redis_conn = redis_conn

    @staticmethod
    def get_key(client_id, interval, method_type):
        '''
        This function returns key to be used in redis.

        '''
        return client_id+"_"+ method_type +"_"+interval;

    def get_key_expiry(self, interval):
        '''
        This function returns key expiry time in seconds.

        '''
        return self.interval_dict.get(interval, 0)

    def check_rate_limit(self, client_id, limits, rate_limit_name):
        '''
        This function checks rate limit.

        '''
        for interval, time_type_limit in limits.iteritems():
            if time_type_limit == 0:
                print "I am continuing"
                continue
            time_key = self.get_key(client_id, interval, rate_limit_name)
            print "Time key %s" %  time_key
            key_expiry = self.get_key_expiry(interval)
            print "Key expiry %s" % key_expiry

            time_val = self.redis_conn.get(time_key)
            print "Time val %s" % time_val
            if time_val == None:
                time_type_limit -= 1;
                self.redis_conn.setex(time_key, key_expiry, str(time_type_limit))
            elif time_val == "0":
                return False;
            else:
                self.redis_conn.decr(time_key);
        return True


if __name__ == "__main__":
    print "I am starting"
    url = sys.argv[1]
    method = sys.argv[2]

    redis_manager = redis_helper.RedisManager(host='localhost', port=6379)
    with open("config/rate_limit.json") as fp:
            config_json = json.load(fp)
    #config_json = redis_manager.get_config_json()
    print "Config json %s" % config_json
    client_id = config_json.get("client")
    rate_limit_obj = RateLimiter(redis_manager.get_connection())
  

    while 1:
        for config in config_json.get("specialization", []):
            rate_limit_type = config.get("type")
            rate_limit_name = config.get("name")
            limits = config.get("limit", {})
            print rate_limit_type, rate_limit_name, limits, client_id
            if rate_limit_type == "METHOD" and rate_limit_name == method:
                if not rate_limit_obj.check_rate_limit(client_id, limits, rate_limit_name):
                    print "Rate limit exceeded for URL %s with method %s" % (url, method)
                else:
                    print "API allowed 1"
            elif rate_limit_type == "API" and rate_limit_name == url:
                if not rate_limit_obj.check_rate_limit(client_id, limits, rate_limit_name):
                    print "Rate limit exceeded for API %s" % (url)
                else:
                    print "API allowed 2"
            break
        break
    #redis_manager.delete_keys(client_id)
    redis_manager.close_connection()

