
# * Intermediate Version of the project
# * Gate Application that will run continuously and will simulate a real gate through the terminal
# * In this version the code will be inserted through keyboard

import argparse
from logging import error

SECRET_LEN = 4

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
# TODO: Send {gateID: __, gateSecret: __}  to the Server and wait for the response

# TODO: verify if the server response is valid
# if valid :
#   print("The secret is valid for this gate")
# else:
#   print("The secret is not valid for this gate") 
#   print("Exiting...")
#   exit

while(1):
    # TODO: read user code
    # Type the user code : ______

    # TODO: Contact Server and receive if user inserted code is valid or not
    # if valid :
    #   print("!!! Code Valid !!!")
    #   print("!!! The gate will close in 6 seconds")
    #   sleep(6)
    # else:
    # print("!!! Code Not Valid !!!")
