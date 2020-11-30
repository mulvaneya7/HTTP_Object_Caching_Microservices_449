Project 6 : HTTP & Object Caching  
author    : Alex Mulvaney
class     : CPSC449 - Back-end Engineering
-------------------------------------------

procfile contents: 
    users: env FLASK_APP=users_microservice.py flask run -p $PORT
    timelines: env FLASK_APP=timelines_microservice.py flask run -p $PORT
    app: env FLASK_APP=flaskr flask run -p $PORT  

.env contents:  
    FLASK_APP=flaskr  
    FLASK_ENV=development  
    debug=True    
    APP_CONFIG=routes.cfg  

commands:
    flask init     #creates the database and adds two Users
    foreman start  #spins up the microservices

timelines_microservice Caching(caching_images.pdf for images):    
    -HTTP Caching: requests made to the "/timelines/all" will cache for 5min returning 304 until 'last-modified' is older than 5min  
    -Object Caching: home timelines will cache post data from the database for 2min before recontacting the db for the same data  


users_microservice.py  
---------------------
this is the users microservice api which allows for users to  
        1) Create Users  
        2) Add/Remove Followers  
        3) Authenticate their account  

USER CREATION AND AUTHENTICATION SERVICES     

urls of interest:  
    -/api/v1/users/createuser [POST] {'username','password','email'}  
    -/api/v1/users/authuser   [authorization] (return JSON {"authorization":bool})

FOLLOWER SERVICES    

urls of interest:
    -/api/v1/users/followers [POST {'username','follow'}, DELETE {'username','remove'}, GET]

timelines_microservice.py
-------------------------
this is the timelines microservice api which allows for users to 
        1) Post Tweets to the public timeline, and fetch the public timeline
        2) retrieve posts made by specific users
        3) retrieve a "home timeline" featuring posts made by users that a username follows

POSTING SERVICES

urls of interest:
    -/api/v1/timelines/postTweet [POST] {'username','content'}

TIMELINE SERVICES

urls of interest:
    -/api/v1/timelines/<username>          [GET] 
    -/api/v1/timelines/all                 [GET] 
    -/api/v1/timelines/home/<username>     [GET]

{ with the current schema.sql these following timeline calls will automatically work:
    foreman start
    http GET :PORT/api/v1/timelines/home/admin
    http GET :PORT/api/v1/timelines/Tweets
    http GET :PORT/api/vq/timelines/all
}

queries/
--------
contains all the PugSql commands

flaskr/
-------
handles the db creation into the instance/ folder