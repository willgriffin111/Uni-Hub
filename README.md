# UniHub

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
## Django Usertypes

Django has different types of users, each with differnt levels of access:

Created using:

```bash
docker exec -it django_app bash
```
This allows you to run commands inside the container^^
```bash
python3 manage.py migrate
```
Idk what this does. The docs told me to do it

```bash
python manage.py create<USERTYPE>
```
The creates the user has a `superuser` (admin).
The other levels are:
1. Admin - `superuser`
2. staff - `staffuser`
3. Regualar - `regularuser`
4. Custom - idk ngl (ask gpt)

Then `exit` to return 
