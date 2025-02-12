# UniHub

These vids pretty good for explaining docker stuff: 
* Mysql container - https://www.youtube.com/watch?v=igc2zsOKPJs&ab_channel=ProgrammingKnowledge
* Docker explained - https://www.youtube.com/watch?v=b0HMimUb4f0&ab_channel=mCoding

To get higer marks we need to use mvc (model, view, controller) - django calles this mtv (model, template, controller). Read this:
https://medium.com/@iamwankang/mvc-pattern-in-django-ef1ca4d1d64e

---  
This project consists of two containers:

* Python (for running Django)
* MySQL (for the database)

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

## Run commands on containers
To access sql container:
```bash
docker exec -it mysql-db bash
```
To access sql server running on sql container (password: rootPassword) 
```bash
docker exec -it mysql-db mysql -u root -p
```
To access Django container:
```bash
docker exec -it django_app bash
```
---
## Django Usertypes

Django has different types of users, each with differnt levels of access:

Created using:

```bash
docker exec -it django-app bash
```
This allows you to run commands inside the container^^
```bash
python3 manage.py migrate
```
Idk what this does. The docs told me to do it

```bash
python manage.py create<USERTYPE>
```
The creates the user with these levels:
1. Admin - `superuser`
2. staff - `staffuser`
3. Regualar - `regularuser`
4. Custom - idk ngl (ask gpt)

Then `exit` to return 
