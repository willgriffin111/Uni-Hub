from django.shortcuts import render
from .database import dbfunc 

def index_view(request):
    print("Loading index page")
    if dbfunc.getConnection():
        status = "Connected to the database"
    else:   
        status = "Failed to connect to the database"
    
        

    
    return render(request, 'index.html', {"db_status": status})
