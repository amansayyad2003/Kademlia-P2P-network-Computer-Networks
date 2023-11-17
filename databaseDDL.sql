drop database if exists MyDatabase;
create database MyDatabase;
use MyDatabase;
create table userInfo(
	username varchar(50),
    fullName varchar(50),
    passwd varchar(50),
    primary key (username)
);
