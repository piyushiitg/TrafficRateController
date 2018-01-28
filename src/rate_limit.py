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
                continue
            time_key = self.get_key(client_id, interval, rate_limit_name)
            key_expiry = self.get_key_expiry(interval)
            

            time_val = self.redis_conn.get(time_key)
            if time_val == None:
                time_type_limit -= 1;
                self.redis_conn.setex(time_key, key_expiry, str(time_type_limit))
            elif time_val == "0":
                return False;
            else:
                self.redis_conn.decr(time_key);
        return True
