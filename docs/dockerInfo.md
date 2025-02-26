# Docker Info

This project consists of two containers:

* Python (for running Django)
* MySQL (for the database)

These vids pretty good for explaining docker stuff: 
* Mysql container - https://www.youtube.com/watch?v=igc2zsOKPJs&ab_channel=ProgrammingKnowledge
* Docker explained - https://www.youtube.com/watch?v=b0HMimUb4f0&ab_channel=mCoding

The `Dockerfile` sets up the Django container, and `docker-compose.yml` runs both together.

The db has the following parameter:
```bash
MYSQL_DATABASE: thedb
MYSQL_USER: rootUser
MYSQL_PASSWORD: password
MYSQL_ROOT_PASSWORD: rootPassword
```
---

## How to run
To start in background (detached):
```bash
docker-compose up -d 
```
To start in terminal:
```bash
docker-compose up
```
If you changed the Dockerfile, add `--build` to rebuild the containers:
```bash
docker-compose up -d --build
```

To stop container:
```bash
docker-compose stop 
```

---
The app should now be running on 

```bash
http://localhost:8000/
```

And admin page on:
```bash
http://localhost:8000/admin
```

---
