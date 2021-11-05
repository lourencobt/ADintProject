
# * Implement REST API to access, manipulate user information in database
# * and implement additional operations

## Errors
# 0 → No error
# 1 → Arguments to create a new gate are not in the correct format
# 2 → ID must be a positive integer.
# 3 → Secret has not the correct secret length.
# 4 → Location has to have a length bigger than 0.
# 5 → There is already a gate with this ID.
# 6 → That is not a valid GateID
# 7 → Couldn't reach GateDataService
# 8 → Incorrect GateDataService response
# 9 → Authentication of the Gate Failed
#10 → Data sent in request was not valid to insert in database

# Imports
from flask import Flask, render_template, request, abort
from flask import json
from flask.json import jsonify
from sqlalchemy import exc
from userDB import updateSecret , newUser, user, updateToken, updateTokenUsed
import random

def generate_code():
    listOfValidCharacters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                             "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6",
                             "7", "8", "9"]

    secretList = []
    for i in range(SECRET_LEN):
        x = random.randint(0, len(listOfValidCharacters)-1)
        secretList.append(listOfValidCharacters[x])

    return ''.join(secretList)

GATEDATASERVICE = "http://localhost:8000/"
SECRET_LEN = 4

app = Flask(__name__)

def raise_error(errorNumber, errorDescription):
    return {"error": errorNumber, "errorDescription":errorDescription}

@app.route("/API/users", methods=['POST'])
def resgistNewUser():

    data = request.json
    
    try:
        id = data["istID"]
    except:
        abort(400)
    if (error := newUser( id )) == 0:
            return { 
                "error": 0
            }
    else:
        return raise_error(1,"Something happened!")
    
@app.route("/API/users/token", methods=['POST'])
def updatToken():

    data = request.json
    try:
        id = data["istID"]
        token = data["token"]
    except:
        abort(400)

    if (error := updateToken( id , token )) == 0:
            return { 
                "error": 0
            }
    else:
        return raise_error(1,"Something happened!")
    
@app.route("/API/users/secret", methods=['POST'])
def updateSecretUser():

    data = request.json
    try:
        id = data["istID"]
        secret = data["secret"]
    except:
        abort(400)
    if (error := updateSecret( id,secret)) == 0:
            return { 
                "error": 0
            }
    else:
        return raise_error(1,"Something happened!")
    
@app.route("/API/users/access", methods=['POST'])
def updatAccess():

    data = request.json  
    try:
        id = data["istID"]
    except:
        abort(400)

    if (error := updateTokenUsed( id )) == 0:
            return { 
                "error": 0
            }
    else:
        return raise_error(1,"Something happened!")




@app.route("/API/users/<istID>")
def getUserInfo(istID):

    users = user(istID).json()

    return jsonify( users.json() )
    
@app.route("/API/users/<istID>/history/")
def getHistory(gateID):
    return

@app.route("/API/users/access", methods=['POST'])
def postHistory(gateID):
    return

if __name__ == "__main__":
    app.run(port=8001, debug=True)