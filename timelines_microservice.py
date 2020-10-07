"""
timelines_microservice.py
---------------------
author: Alex Mulvaney
class : CPSC449 - Backend Development
desc  :
        this is the timelines microservice api which allows for users to 
        1) Post Tweets to the public timeline, and fetch the public timeline
        2) retrieve posts made by specific users
        3) retrieve a "home timeline" featuring posts made by users that a username follows

"""

from flask import Flask, url_for, request, json, Response, jsonify, abort
from datetime import datetime
import pugsql
import logging
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["DEBUG"]=True

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
def jsonifyTimeline(query):
    jsonversion = {}
    i = 0
    for each in query:
        jsonversion[i] = {'username': each['username'], 'content': each['content'], 'date': each['dateot']}
        i+=1
    return jsonify(jsonversion)


#This service will return a "timeline" of posts in JSON
@app.route('/api/v1/timelines/all', methods=['GET'])
def getPublicTimeline():
    allTimeline = queries.get_all_tweets()
    return jsonifyTimeline(allTimeline), 200

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
    homeTimeline = queries.get_home_timeline(usernames_=is_following_list)
    return jsonifyTimeline(homeTimeline), 200
    

# if __name__ == '__main__':
#     app.run()