
# * Intermediate Version of the project
# * Gate Application that will run continuously and will simulate a real gate through the terminal
# * In this version the code will be inserted through keyboard

import argparse
from logging import error
import requests
import time

SECRET_LEN = 4
SERVICE = "http://172.30.209.117:8001/"

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
  if r.json()['valid'] :
    print("The secret is valid for this gate")
  else:
    print("The secret is not valid for this gate") 
    print("Exiting...")
    exit(-1)
except:
  print("Couldn't connect to the server")
  print("Exiting...")
  exit(-2)

while(1):
    # Read user code
    userCode = input("Type the user code: ")
    if userCode == 'q':
        exit(0)

    # Contact Server and receive if user inserted code is valid or not
    try:
      r = requests.post(SERVICE+"/API/gates/{}/code".format(gateDict["gateID"]), json={"code":userCode})
    except:
      print("Couldn't connect to the server")
      continue
    try:
      data = r.json()
      if data['valid'] :
        print("!!! Code Valid !!!")
        print("!!! The gate will close in 6 seconds")
        time.sleep(6)
      else:
          print("!!! Code Not Valid !!!")
    except:
      print("Bad server response")
      continue

