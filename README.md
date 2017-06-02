# HindSite

Python web regression testing software

#requirements

//todo

#How to

clone the repository

run `mysql -uroot -p -Dhindsite < "skeletondb.sql"` to get the tables into your database

run `xvfb-run --server-args="-screen 0 1920x1080x24+32 -ac" -a rq worker` to start up a redis worker

run `gunicorn --bind 0.0.0.0:8080 main:app` to start up the server

//todo: make the readme less awful
