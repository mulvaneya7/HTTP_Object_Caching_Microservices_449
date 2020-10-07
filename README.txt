Project 2 : Microservices  
author    : Alex Mulvaney
class     : CPSC449 - Back-end Engineering
-------------------------------------------

commands:
    flask init     #creates the database and adds two Users(cannot authenticate these two users because password_hash isnt called on them, you can authenticate newly created users though)
    foreman start  #spins up the microservices


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