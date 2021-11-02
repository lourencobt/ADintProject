
# * Intermediate Version of the project
# * User application in this version will only show a simple alphanumeric code

import requests

SERVICE = "http://localhost:8001/"
print("Contacting Server ...")

# Request Code
try: 
    r = requests.get(SERVICE+"/API/users/joao/code")
except:
    print("Couldn't connect to the server")
    print("Exiting...")
    exit(-1)

# Verify if Code was received and was valid
if r.status_code == 200:
    try:
        error = r.json()["error"]
    except:
        print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin.")
        print("Exiting...")
        exit(-2)
    if error == 0:
        try: 
            code = r.json()["code"]
        except:
            print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin")
            print("Exiting...")
            exit(-3)
        
        print("Code received")
        print(">>> "+ code +" <<<")
        print("Please type the code in the Gate")
    else:
        print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin [ERROR CODE {}]".format(error))
        print("Exiting...")
        exit(-4)
else:
    print("Request wasn't successful.")
    print("Exiting...")
    exit(-5)