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

**Amazon example:**
![image](https://github-production-user-asset-6210df.s3.amazonaws.com/52665298/340826529-b25ffa78-cad0-4af8-8d84-0d8b49997147.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20240618%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240618T210959Z&X-Amz-Expires=300&X-Amz-Signature=f8e741dce0d6b122f89a355ec22239faa3db30c3a80fc9d3d8cd16cefc33ac00&X-Amz-SignedHeaders=host&actor_id=52665298&key_id=0&repo_id=817007793)
Amazon is telling the database management system to alter the database

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

---

[^1]: two or more events happening at the same time