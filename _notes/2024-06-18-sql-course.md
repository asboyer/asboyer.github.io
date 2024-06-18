---
layout: post
date: 2024-06-18 05:00:00
time: 9:44pm
location: Lisbon, Portugal
inline: false
related_posts: false
title: sql notes
giscus_comments: true
unfinished: true
---
---
Notes from [SQL Tutorial - Full Database Course for Beginners](https://www.youtube.com/watch?v=HXV3zeQKqGY)

---
#### What is a Database (DB)?
- a collection of related information
- databases can be stored in different ways

Computers + Databases = <3
: computers are great at keeping track of large amounts of information

Database management Systems (DBMS)
: a special software program that helps users create and maintain a database
* makes it easy to manage large amounts of information
* handles security, backups, imports/exports, concurrency[^1]
* interact with software applications, ex: programming languages

Amazon will tell the database management system to alter the database

#### **C.R.U.D**: Create, Read, Update, Delete
* Creating new entries
* Retrieving
* Updating
* Deleting

Core 4 operations \
Any good DBMS can do these things

#### Two types of Databases
* **Relational databases (SQL)**
    * organize data into one or more tables
    * a unique key identifies each row
* **Non-Relational databases (noSQL)**
    * organize data in anything but a table 
    * key value stores
    * documents
    * `json`, `xml`, graphs

#### **Relational databases**
![image](/assets/img/notes/relational.png)

Can use a relational database management system (RDBMS)
* helps users create and maintain a relational database
* ex: mySQL, Oracle, postgreSQL, etc.

#### Structured Query Language (SQL)
* standardized lang for interacting with RDBMS
* used to perform CRUD operations
* define tables and structures
* SQL code used on one RDBMS may not be usable on another

---

[^1]: two or more events happening at the same time