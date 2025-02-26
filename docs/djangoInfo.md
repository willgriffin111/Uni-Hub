# Django info

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

To create new app:
```bash
docker exec -it django-app python manage.py startapp <NAME>
```
> **_NOTE:_** I did `docker exec -it django-app python manage.py startapp accounts` to make the accounts app
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
