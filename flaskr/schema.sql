PRAGMA foreign_keys = ON;
drop table if exists Users;
drop table if exists Followers;
drop table if exists Tweets;
CREATE TABLE "Users" (
    "Username"TEXT NOT NULL UNIQUE,
    "Pass"TEXT NOT NULL,
    "Email"TEXT,
    PRIMARY KEY("Username")
);
CREATE TABLE "Followers" (
	"username"	TEXT,
	"followingUser"	TEXT
);
CREATE TABLE "Tweets" (
	"username"	TEXT,
	"content"	TEXT,
	"dateot"	TEXT,
	"idot"	INTEGER PRIMARY KEY AUTOINCREMENT
);
INSERT INTO Users values ("admin", "password", "admin@admin.com");
INSERT INTO Users values ("test", "test", "test@admin.com");
INSERT INTO Followers values ("admin", "test");
INSERT INTO Tweets values ("test", "is this thing on?...", "111111", 0)
