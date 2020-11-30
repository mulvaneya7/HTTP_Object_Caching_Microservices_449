"""
timelines_microservice.py
updated: project 6: CACHING (HTTP and Object caching)
---------------------
author: Alex Mulvaney
class : CPSC449 - Backend Development
desc  :
        this is the timelines microservice api which allows for users to 
        1) Post Tweets to the public timeline, and fetch the public timeline
        2) retrieve posts made by specific users
        3) retrieve a "home timeline" featuring posts made by users that a username follows
        updated caching:
        HTTP caching)   requests made to the "/timelines/all" will cache for 5min returning 304 until 'last-modified' is older than 5min
        Object caching) home timelines will cache post data from the database for 2min before recontacting the db for the same data

"""

from flask import Flask, url_for, request, json, Response, jsonify, abort
from datetime import datetime, date, timedelta
from flask_caching import Cache
from operator import itemgetter
import pugsql
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from utils import docache

app = Flask(__name__)
app.config["DEBUG"]=True
app.config['CACHE_TYPE']='simple'
app.config['CACHE_DEFAULT_TIMEOUT']=300

#setting the cache
cache = Cache(app)

#Setting up the pugsql modules to point at our queries folder with our sql commands. Then connect to our SQLite DB
queries = pugsql.module('queries/')
queries.connect('sqlite:///instance/flaskr.sqlite')

'''
POSTING SERVICES

urls of interest:
    -/api/v1/timelines/postTweet [POST] {'username','content'}
'''

#HELPER FUNCTION
def existing_user(username):
    user = queries.get_user(username_=username)
    if user is None:
        return False
    else:
        return True

#This service will recieve JSON for a post(tweet) and add it to the public "timeline"
@app.route('/api/v1/timelines/postTweet', methods=['POST'])
def postTweet():
    if request.headers['Content-Type'] == 'application/json':
        username = request.json.get('username')
        content = request.json.get('content')
        if username is None or content is None or not existing_user(username):
            abort(400) #(BAD REQUEST: no username or content attached or user does NOT exist)
        queries.add_post(username_=username, content_=content, dateot_=datetime.now())
        return jsonify({'posted':datetime.now()}), 201
    else:
        abort(415) #(UNSUPPORTED MEDIA TYPE)

'''
TIMELINE SERVICES

urls of interest:
    -/api/v1/timelines/<username>          [GET]
    -/api/v1/timelines/all                 [GET]
    -/api/v1/timelines/home/<username>     [GET]
'''

#HELPER FUNCTION
#turns queries from the Tweets table into nice json
def jsonifyTimeline(query_):
    jsonversion = {}
    i = 0
    for each in query_:
        jsonversion[i] = {'username': each['username'], 'content': each['content'], 'date': each['dateot']}
        i+=1
    return json.dumps(jsonversion)


#This service will return a "timeline" of posts in JSON 
@app.route('/api/v1/timelines/all', methods=['GET'])
def getPublicTimeline():
    #check request modified, return 304 on requests younger than 5min
    if 'If-Modified-Since' in request.headers:
        date_time_obj = datetime.strptime(request.headers['If-Modified-Since'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() < date_time_obj + timedelta(minutes=5):
            return Response(status=304)
    allTimeline = queries.get_all_tweets()
    minutes = 5
    then = datetime.now() + timedelta(minutes=minutes)
    rsp = Response(jsonifyTimeline(allTimeline), content_type='application/json')
    #rsp.headers.add('Expires', then.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    rsp.headers.add('Last-Modified', datetime.now())
    #rsp.headers.add('Cache-control', 'public,max-age=%d' % int(60 * minutes))
    return rsp

#This service will return a "timeline" of posts made by a username
@app.route('/api/v1/timelines/<username>', methods=['GET'])
def getUserTimeline(username):
    if not existing_user(username):
        abort(404) #(NOT FOUND: user doesnt exist)
    userTimeline = queries.get_user_timeline(username_=username)
    return jsonifyTimeline(userTimeline), 200

#This service will take a username from the url and return a "timeline" of posts
#made by users the username follows in JSON.
@app.route('/api/v1/timelines/home/<username>', methods=['GET'])
def getHomeTimeline(username):
    #query: return list of users the username is following in reverse chrono order
    is_following = queries.get_all_following(username_=username)
    is_following_list = []
    #for: extracting users' info to list form
    for each in is_following:
        is_following_list.append(each['followingUser'])
    #query: return all posts made by users the username is following in reverse chrono order
    #homeTimeline = queries.get_home_timeline(usernames_=is_following_list)
    '''
    create a hometimeline list that caches data for 2min after each call
    '''
    homeTimeline = []
    for each in is_following_list:
        if(cache.get(each) == None):
            tweetlist = list(queries.get_user_timeline(username_=each))
            cache.set(each, tweetlist)
            app.logger.debug(f"homeTimeline data from db user: {each}")
        else:
            app.logger.debug(f"homeTimeline data from cache user: {each}")
        homeTimeline.extend(cache.get(each))
    sortedTimeline = sorted(homeTimeline, key=itemgetter('dateot'), reverse=True)    
    rsp = Response(jsonifyTimeline(sortedTimeline), content_type='application/json')
    rsp.headers.add('Last-Modified', datetime.now())
    return rsp
    


# if __name__ == '__main__':
#     app.run()