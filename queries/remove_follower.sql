-- :name remove_follower
DELETE FROM Followers WHERE username = :username_ AND followingUser = :usernameToRemove_