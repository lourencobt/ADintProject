
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

#11 → Arguments to create a new user are not in the correct format
#12 → There is already a user with this ID.
#13 → That is not a valid user
#14 → No history for this user
#15 → Gate doesn't exist

# Imports
from flask import Flask, render_template, request, abort
from flask import json
from flask.json import jsonify
from sqlalchemy import exc
from userDB import listHistory, listUserHistory, listUsersId, newHistory, updateSecret , newUser, userInfor, updateToken, updateSecretUsed
import random
from datetime import datetime

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


#Creates the token for the session
#Changes the previous token if exists already and 
#changes the validation of the token to True
@app.route("/API/users/<path:istID>/token", methods=['POST'])
def updatToken(istID):

    data = request.json
    try:
        id = istID
        token = data["token"]
    except:
        abort(400)

    if (error := updateToken( id , token )) == 0:
        return { 
            "error": 0
        }
    elif error == -1:
        return raise_error(13,"This is not a valid user")
    else:
        return raise_error(1,"Something happened!")
    
#Updates the secret after being created the QRCode
#The user must exist in order to create this QRCode
@app.route("/API/users/<path:istID>/secret", methods=['POST'])
def updateSecretUser(istID):
    data = request.json
    try:
        id = istID
        secret = data["secret"]
    except:
        abort(400)

    if (error := updateSecret(id,secret)) == 0:
        return { 
            "error": 0
        }
    elif error == -1:
        return raise_error(13,"That is not a valid user")
    elif error == -2:
        return raise_error(10,"Data sent in request was not valid to insert in database")
    else:
        return raise_error(1,"Something happened!")
    

@app.route("/API/users/<path:istID>/invalid", methods=['POST'])
def updateAccessInvalid(istID):
    try:
        id = istID
    except:
        abort(400)

    if (error := updateSecretUsed( id )) == 0:
            return { 
                "error": 0
            }
    elif error == -1:
        return raise_error(13,"That is not a valid user")
    elif error == -2:
        return raise_error(10,"Data sent in request was not valid to insert in database")
    else:
        return raise_error(1,"Something happened!")

@app.route("/API/users", methods=['POST'])
def resgistNewUser():
    data = request.json
    try:
        id = data["istID"]
        token = data["token"]
    except:
        abort(400)

    if (error := newUser( id, token )) == 0:
            return { 
                "error": 0
            }
    elif error == -1:
        return raise_error(10,"Data sent in request was not valid to insert in database")
    elif error == -2:
        return raise_error(11,"There is already a user with this ID.")
    else:
        return raise_error(100, "Something went wrong")
    
@app.route("/API/users/<path:istID>")
def getUserInfo(istID):
    userInfo = userInfor(istID)   
    if userInfo == None:
        return {
            "userInfo": None, 
            "error": 0
        }
    else:
        return {
            "userInfo":  {
                        "istID": userInfo.id,
                        "secret": userInfo.secret,
                        "token": userInfo.token, 
                        "valid": userInfo.valid,
                        "dateSecret" : str(userInfo.datesecret)
                        },
            "error": 0
        }
        
#Get all the history from a specific user
@app.route("/API/users/<path:istID>/history")
def getHistory(istID):
    
    history = listUserHistory(istID)   
    allHistory = []
    
    try:
        for i in history:
            allHistory.append({"istID": i.istID, 
                            "gateID": i.gateID,
                            "date": i.date 
                            })
    except:
        return raise_error(12 ,"That is not a valid user")

    
    return {
        "historyList": allHistory, 
        "error": 0
    }

#Post an activity of a user
@app.route("/API/users/access", methods=['POST'])
def postHistory():
    
    data = request.json  

    try:
        istID = data["istID"]
        gateID = int(data["gateID"])
        date = datetime.fromisoformat(data["date"])
    except:
        abort(400)

    if (error := newHistory(istID,gateID,date)) == 0:
            return { 
                "error": 0
            }
    elif error == -1:
        return raise_error(11,"Arguments to create a new history are not in the correct format")
    elif error == -2:
        return raise_error(6,"GateID not valid")
    elif error == -3:
        return raise_error(13,"Date not valid")
    elif error == -4:
        return raise_error(10,"Data sent in request was not valid to insert in database")
    else:
        return raise_error(1,"Something happened!")
  
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8002, debug=True)