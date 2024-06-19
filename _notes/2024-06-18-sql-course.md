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
notebook: true
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

SQL is the standard in relational databases

#### **Non relational**
![image](/assets/img/notes/non_relational.png)

Management systems:
* MongoDB, firebase, etc.
* implementation specific -> no standard language

#### Database queries
Queries
: are requests made to the database management system for specific information \
As the structure becomes more complex, it becomes more difficult to get specific pieces of information

---

Tables
: Have columns, rows

Columns
: categories

Rows
: a single entry

Primary key
: uniquely defines a row

![image](/assets/img/notes/primary_key.png)
How to discern between the Jacks?

*Primary key* is different. *Always* going to be unique for each row in the table

Can be anything (str, int, etc.), as long as its unique

#### Types of Primary keys

1. Surrogate key
: key that has no mapping to anything in real world (random)

2. Natural key
: ex: social security number

3. Foreign key
: stores the primary key of a row in another database table

#### Foreign key example:
`branch_id` maps to a row in the **Branch** database
![image](/assets/img/notes/foreign_key_1.png)
![image](/assets/img/notes/foreign_key_2.png)

**Note**: can have multiple foreign keys \
Can also use foreign key to map to another row in the same table \
Can define a **composite key** to define a key that uses multiple columns to combine to make a primary key. \
ie: two columns uniquely defining a row to make a primary key

---

[^1]: two or more events happening at the same time