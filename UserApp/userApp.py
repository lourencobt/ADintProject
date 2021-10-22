
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
        data = r.json()
        print("Code received")
        print(">>> "+ data["code"] +" <<<")
        print("Please type the code in the Gate")
    except:
        print("Request wasn't successful.")
        print("Exiting...")
        exit(-2)
else:
    print("Request wasn't successful.")
    print("Exiting...")
    exit(-3)