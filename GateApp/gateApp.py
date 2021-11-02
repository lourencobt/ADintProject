
# * Intermediate Version of the project
# * Gate Application that will run continuously and will simulate a real gate through the terminal
# * In this version the code will be inserted through keyboard

import argparse
from logging import error
import requests
import time

SECRET_LEN = 4
SERVICE = "http://localhost:8001/"

# Parsing arguments
def secret(string):
    if(len(string) != SECRET_LEN):
        raise error
    return string

parser = argparse.ArgumentParser(description="Gate Application that will run continuously and will simulate a real gate through the terminal")
parser.add_argument('gateID', nargs=1, type=int, help="an integer corresponding to the ID of the gate")
parser.add_argument('gateSecret', nargs=1, type=secret, help="a String with %d characters corresponding to the Secret of the gate" % (SECRET_LEN))
args = parser.parse_args()

gateDict = {"gateID": args.gateID[0], "gateSecret": args.gateSecret[0]}

print("Contacting Server ...")

# Send {gateID: __, gateSecret: __}  to the Server and wait for the response
# verify if the server response is valid
try: 
  r = requests.post(SERVICE+"/API/gate", json=gateDict)
except:
  print("Couldn't connect to the server. Try again later or contact the admin")
  print("Exiting...")
  exit(-1)

if r.status_code == 200:
  try:
    error = r.json()["error"]
  except:
    print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin")
    print("Exiting...")
    exit(-2)
  
  if error == 0:
    try:
      valid = r.json()['valid']
    except:
      print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin")
      print("Exiting...")
      exit(-3)

    if valid :
        print("The secret is valid for this gate")
    else:
      print("The secret is not valid for this gate") 
      print("Exiting...")
      exit(-4)
  elif error == 6:
    print("That is not a valid gateID.")
    exit(-5)
  else: 
    print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin [ERROR CODE {}]".format(error))
    exit(-5)
else:
  print("Bad Request. Contact the admin.")
  print("Exiting...")
  exit(-6)

while(1):
    # Read user code
    userCode = input("Type the user code: ")
    if userCode == 'q':
        exit(0)

    # Contact Server and receive if user inserted code is valid or not
    try:
      r = requests.post(SERVICE+"/API/gates/{}/code".format(gateDict["gateID"]), json={"code":userCode, "secret":gateDict["gateSecret"]})
    except:
      print("Couldn't connect to the server. Try again later or contact the admin")
      print("Exiting...")
      exit(-7)
      
    if r.status_code == 200:
      try:
        error = r.json()["error"]
      except:
        print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin")
        continue
      
      if error == 0:
        try:
          valid = r.json()['valid']
        except:
          print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin")
          continue
        
        if valid:
          print("!!! Code Valid !!!")
          print("!!! The gate will close in 6 seconds")
          time.sleep(6)
        else:
          print("!!! Code Not Valid !!!")
      else:
        print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin [ERROR CODE {}]".format(error))
    else:
      print("Invalid Server Response. Server not working for the moment. Try again later or contact the admin")  
          
      


