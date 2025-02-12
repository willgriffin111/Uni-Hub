#Alex Rogers22018703

import mysql.connector
from mysql.connector import errorcode
import os
 
# MYSQL CONFIG VARIABLES 

#idk why this isnt working man - alex 2023 
# hostname    = "127.0.0.1"
# username    = "rootUser"
# passwd  = "password"
# db = "uniHub"

hostname = os.getenv('DB_HOST', 'db')
username = os.getenv('DB_USER', 'rootUser')
passwd = os.getenv('DB_PASSWORD', 'password')
db = os.getenv('DB_NAME', 'uniHub')
    

def getConnection():  
    try:
        conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              database=db)  
        print('Connected to the database!!!!!')
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            return err                    
    # else:  #will execute if there is no exception raised in try block
    #     return conn   
                