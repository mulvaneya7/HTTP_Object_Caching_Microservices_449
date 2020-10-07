-- :name add_follower :insert
insert into Followers (username, followingUser) values (:username_, :followingUser_)
