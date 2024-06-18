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
![image](https://private-user-images.githubusercontent.com/52665298/340844366-287adb8d-85f0-48d4-b4ca-98d26110f5da.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTg3NDcxOTcsIm5iZiI6MTcxODc0Njg5NywicGF0aCI6Ii81MjY2NTI5OC8zNDA4NDQzNjYtMjg3YWRiOGQtODVmMC00OGQ0LWI0Y2EtOThkMjYxMTBmNWRhLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA2MTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNjE4VDIxNDEzN1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTU2ZjkzMGQwNmI4ZThhZDI4OTY3NmM5MDczZDY4NDAxMTU0YjExYmJlZmE5MzlmMDM3MjU1YTJhNmQzNzJiYjUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.PXSzitjkL9f9W21v7uF108mrmo9i8SSdxJRhw8YH-3M)
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