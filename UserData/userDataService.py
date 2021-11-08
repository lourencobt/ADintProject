
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
#16 → Date doesn't exist

# Imports
from flask import Flask, render_template, request, abort
from flask import json
from flask.json import jsonify
from sqlalchemy import exc
from userDB import listHistory, listUserHistory, newHistory, updateSecret , newUser, userInfor, updateToken, updateTokenUsed
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


#Functions not defined in "Try Notion"!!!
#Features are defined before functions and their porpuse are 
# #to help with other aspects and manipulate the database

#Creates the token for the session
#Changes the previous token if exists already and 
#changes the validation of the token to True
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
    elif error == -1:
        return raise_error(13,"This is not a valid user")
    else:
        return raise_error(1,"Something happened!")
    
#Updates the secret after being created the QRCode
#The user must exist in order to create this QRCode
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
    elif error == -1:
        return raise_error(13,"That is not a valid user")
    elif error == -2:
        return raise_error(10,"Data sent in request was not valid to insert in database")
    else:
        return raise_error(1,"Something happened!")
    
#Put the token in invalid mode
#Change the boolean to False
@app.route("/API/users/invalid", methods=['POST'])
def updatAccessInvalid():

    data = request.json  
    try:
        id = data["istID"]
    except:
        abort(400)

    if (error := updateTokenUsed( id )) == 0:
            return { 
                "error": 0
            }
    elif error == -1:
        return raise_error(13,"That is not a valid user")
    elif error == -2:
        return raise_error(10,"Data sent in request was not valid to insert in database")
    else:
        return raise_error(1,"Something happened!")



#Functions defined in "Try Notion"!!!
#Supposly they are complete but they need a few features
#Check them!!!!!!!!!!!!!!!!!!!

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
    elif error == -1:
        return raise_error(11,"Arguments to create a new user are not in the correct format.")
    elif error == -2:
        return raise_error(12,"There is already a user with this ID.")
    else:
        return raise_error(100, "Something went wrong")
    
@app.route("/API/users/<path:istID>")
def getUserInfo(istID):

    userInfo = userInfor(istID)   
    userInformation = []
    
    try:
        userInformation.append({"success": userInfo.id, 
                        "secret": userInfo.secret,
                        "token": userInfo.token, 
                        "valid": userInfo.valid
                        })
    except:
        return raise_error(13 ,"That is not a valid user")

    
    return {
        "userInfo": userInformation, 
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
        return raise_error(13 ,"That is not a valid user")

    
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
        gateID = data["gateID"]
        date = data["date"]
    except:
        abort(400)

    try:
        date = datetime.strptime(date,"%d/%m/%y %H:%M")
    except:
        return raise_error(16,"Date not valid : format 21/11/06 16:30 dd/mm/yyyy HH:MM")

    if (error := newHistory(istID,gateID,date)) == 0:
            return { 
                "error": 0
            }
    elif error == -1:
        return raise_error(11,"Arguments to create a new user are not in the correct format")
    elif error == -2:
        return raise_error(15,"Gate doesn't exist")
    elif error == -3:
        return raise_error(16,"Date not valid : format 21/11/06 16:30 dd/mm/yyyy HH:MM")
    elif error == -4:
        return raise_error(10,"Data sent in request was not valid to insert in database")
    else:
        return raise_error(1,"Something happened!")

    return 

if __name__ == "__main__":
    app.run(port=8001, debug=True)