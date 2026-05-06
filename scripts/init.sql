CREATE DATABASE db;

USE db;

CREATE TABLE users (
    userid INTEGER NOT NULL AUTO_INCREMENT,
    mbo VARCHAR(50) UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    mobile VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    surname VARCHAR(200) NOT NULL,
    receive_by_sms INTEGER NOT NULL,
    receive_by_email INTEGER NOT NULL, 
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY(userid)
);

INSERT INTO users VALUES (
    0,
    "123",
    "ltestiranje",
    "$2y$12$0B7nBuL7U3VqsR8DL1xAZOlNad/1Z2UVqP2zC92LkgGJMcP1Ge2yi",
    "luka.testiranje@proton.me",
    "+385 98 000 0000",
    "Luka",
    "Testiranje",
    1,
    1,
    "patient"
);

INSERT INTO users VALUES (
    0,
    "456",
    "mtestiranje",
    "$2y$12$ANu33AycpXvP5MeinBS.JeXYLhGcxBtTGAY5RpUfVcX1.NZRKqUQu",
    "mia.testiranje@proton.me",
    "+385 98 000 0001",
    "Mia",
    "Testiranje",
    1,
    1,
    "provider"
);

CREATE TABLE perscriptions (
    perscriptionid INTEGER NOT NULL AUTO_INCREMENT,
    userid INTEGER NOT NULL,
    drugname VARCHAR(200) NOT NULL,
    consume_times JSON,
    pickup_again DATE,
    PRIMARY KEY (perscriptionid)
);