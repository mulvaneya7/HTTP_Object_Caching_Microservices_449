-- :name get_all_following :many
select followingUser from followers where username = :username_