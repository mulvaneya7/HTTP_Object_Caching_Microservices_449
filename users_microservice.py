"""
users_microservice.py
---------------------
author: Alex Mulvaney
class : CPSC449 - Backend Development
desc  :
        this is the users microservice api which allows for users to 
        1) Create Users
        2) Add/Remove Followers
        3) Authenticate their account

"""

from flask import Flask, url_for, request, json, Response, jsonify, abort
import pugsql
import logging
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["DEBUG"]=True

#Setting up the pugsql modules to point at our queries folder with our sql commands. Then connect to our SQLite DB
queries = pugsql.module('queries/')
queries.connect('sqlite:///instance/flaskr.sqlite')


'''
USER CREATION AND AUTHENTICATION SERVICES

urls of interest:
    -/api/v1/users/createuser [POST] {'username','password','email'}
    -/api/v1/users/authuser   [authorization]
'''

@app.route('/api/v1/users/createuser', methods=['POST'])
def createuser():
    if request.headers['Content-Type'] == 'application/json':
        username = request.json.get('username')
        password = generate_password_hash(request.json.get('password'))
        email = request.json.get('email')
        if username is None or password is None:
            abort(400) #this abort happens if a username or password is not inserted (BAD REQUEST)
        #Insert into the database using PugSql methods
        queries.create_user(username_=username, pass_=password, email_=email)
        #return 201 (CREATED) with the the new user's username
        return jsonify({'username': username}), 201
    else:
        abort(415) #unsupported media type

def check_auth(username, password):
    user = queries.get_user(username_=username)
    if user is None:
        abort(404) #(NOT FOUND: user doesnt exist)
    else:
        return check_password_hash(user['Pass'], password)


@app.route('/api/v1/users/authuser')
def auth_user():
    auth = request.authorization
    if not auth:
        abort(400) #(BAD REQUEST)
    else:
        cred = check_auth(auth.username, auth.password)
        return jsonify({'authorized': cred})


'''
FOLLOWER SERVICES

urls of interest:
    -/api/v1/users/followers [POST {'username','follow'}, DELETE {'username','remove'}, GET]
'''

def addFollower(username, usernameToFollow):
    queries.add_follower(username_=username, followingUser_=usernameToFollow)

def removeFollower(username, usernameToRemove):
    queries.remove_follower(username_=username, usernameToRemove_=usernameToRemove)

@app.route('/api/v1/users/followers', methods=['POST', 'DELETE', 'GET'])
def FollowerUpdate():
    #get the username of interest
    username = request.json.get('username')
    if username is None:
        abort(400) #(BAD REQUEST: no username)

    #POST -- ADDING a FOLLOWER
    if request.method == 'POST':
        usernameToFollow = request.json.get('follow')
        if usernameToFollow is None:
            abort(400) #(BAD REQUEST: no username to follow)
        addFollower(username, usernameToFollow)
        return jsonify({'username': username, 'follow':usernameToFollow}), 201
    #DELETE -- REMOVING a FOLLOWER
    elif request.method == 'DELETE':
        usernameToRemove = request.json.get('remove')
        if usernameToRemove is None:
            abort(400) #(BAD REQUEST: no username to remove from following)
        removeFollower(username, usernameToRemove)
        return jsonify({'username': username, 'remove':usernameToRemove}), 200
    #GET -- GET all FOLLOWING list
    elif request.method == 'GET':
        following_list = queries.get_all_following(username_=username)
        index = 0
        formattedList = {}
        for follower in list(following_list):
            formattedList[index] = follower['followingUser']
            index += 1

        app.logger.info(formattedList)
        return jsonify(formattedList), 200
                
    else:
        abort(400) #(BAD REQUEST)
    


# if __name__ == '__main__':
#     app.run()