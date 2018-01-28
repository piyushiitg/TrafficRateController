import redis
class RedisManager(object):
    '''
    This class provides methods to manage redis server.

    '''
    def __init__(self, host, port):
        self.redis_conn = redis.StrictRedis(host=host, port=port, db=0)

    def get_connection(self):
        '''
        This function returns redis connection

        '''
        return self.redis_conn

    def close_connection(self):
        '''
        This function closes connection with redis server.

        '''
        try:
            del self.redis_conn
        except Exception, ex:
            print "Exception in closing connection", ex

    def delete_keys(self, pattern):
        '''
        This function deletes all the keys matching the pattern.

        '''
        try: 
            print "Deleting Keys" , pattern
            x = self.redis_conn.keys(pattern + "*") 
            for key in x: 
                self.redis_conn.delete(key)
        except Exception, err:
            print "Exception", err

    def get_config_json(self):
        try:
            config_dict = self.redis_conn.get("rate_limit")
            return eval(config_dict) #TODO
        except:
            return {}

    def set_key(self, key, value):
        try:
            self.redis_conn.set(key, value)
        except:
            pass
