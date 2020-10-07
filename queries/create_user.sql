-- :name create_user :insert
insert into Users (Username, Pass, Email) values (:username_, :pass_, :email_)
