# TrafficRateController
Traffic Shaping
This is traffic shaping program provides rate limiting feature using rate_limit.json file present in config/ folder. This is project uses python redis to connect to Redis, Flask for API.

Currently when rate limit hits, platform returns 429 response code with message as "Rate limit exceeded, wait for sometime."

Setup

# Installation
1. pip install flask
2. pip install flask-api
3. pip install flask-restful 
4. pip install redis


How to Run:
1. Git Clone this repository

2. Download redis server from https://redis.io and make sure it is running on localhost and on port 6379. or you can follow below steps to install redis
# Redis Server Installation
1. mkdir redis && cd redis
2. curl -O http://download.redis.io/redis-stable.tar.gz
3. tar xzvf redis-stable.tar.gz
4. cd redis-stable
5. make
6. make test
7. sudo make install

3. Run app.py file which is present src/
cd src/
python app.py

This will start the application.
Currently there are 3 apis present in the project, /pay, /status, /check, which can be used to test the ratelimit thing.
Current configuration of rate limit is present in rate_limit.json at src/config. If you change anything in this, please restart the application to take the effect of new rate_limit.json file. After restart code will delete older keys from redis, you can comment this if not required.




