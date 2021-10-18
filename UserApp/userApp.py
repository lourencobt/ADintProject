
# * Intermediate Version of the project
# * User application in this version will only show a simple alphanumeric code

import requests

print("Contacting Server ...")

# TODO: Request Code
try: 
    r = requests.get("http://172.30.220.58:8000/users/joao")
except:
    # ! Should we do except to a especific exception?
    print("Request wasn't successful.")
    print("Exiting...")
    exit(-1)

# TODO: Verify if Code was received and was valid
if r.status_code == 200:
    data = r.json()

    print("Code received")
    print(">>> "+ data["code"] +" <<<")
    print("Please type the code in the Gate")