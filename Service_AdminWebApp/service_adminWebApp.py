
# * Intermediate Version of the project
# * This program has 2 purposes. It consist in the service + adminWebApp
# *     - Service:
# *         is composed of a set of REST endpoints that allow UserApp
# *         and GateApp to interact with the system
# *     - AdminWebApp:
# *         composed by two web pages, one for "Registration of a new gate" 
# *         and the other for "Listing registered gates"

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
import os
from flask import Flask, render_template, request, abort, redirect, session
from flask.json import jsonify
import datetime 
import requests

GATEDATASERVICE = "http://localhost:8000/"
SECRET_LEN = 4

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

def raise_error(errorNumber, errorDescription):
    return {"error": errorNumber, "errorDescription":errorDescription}



app = Flask(__name__)

# * User Web App Endpoints implementation
# WEB


# * Gate Web App + Service Endpoints implementation
# WEB
@app.route("/gateApp/WEB/", methods=["GET", "POST"])
def gateApp():
    if request.method == "GET":
        return render_template("authenticateGate.html", secret_len = SECRET_LEN)
    elif request.method == "POST":
        data = request.form
        try:
            gateID = data["gateID"]
            gateSecret = data["secret"]
        except:
            abort(400)

    # Do request to the DB
    try:
        r = requests.post(GATEDATASERVICE+"/API/gates/{}/secret".format(gateID), json={"secret": gateSecret})
    except:
        return "Server is down for the moment. Try again later."

    print(r.json())
    if r.status_code == 200:
        try:
            error = r.json()["error"]
        except:
            return "Error: Something went wrong in Server Response"
        
        if error == 0:
            try:
                valid = r.json()["valid"]
            except:
                return "Error: Something went wrong in Server Response"

            if valid == True:
                session["gateSecret"] = gateSecret
                return render_template("scanner.html", gateID = gateID)
            else:
                return render_template("authenticateGate.html", secret_len = SECRET_LEN, message = "")
        elif error > 0:
            try:
                errorDescription = r.json()["errorDescription"]
            except:
                return "Error: Something went wrong in Server Response"
            
            return "Error: " + errorDescription
    else:
        abort(r.status_code)

# API
# for the Gate to verify if a code is valid
@app.route("/gateApp/API/gates/<path:gateID>/code", methods=['POST'])
def verifyCode(gateID):
    print(session["gateSecret"])
    data = request.json
    print(data)
    try:
        istID = data["istID"]
        gateSecret = session["gateSecret"]
        inserted_code = data["secret"]
    except:
        abort(400)

    JoaoCode = {}
    JoaoCode['code'] = "qmsj"
    JoaoCode['datetime'] = datetime.datetime.now()

     # TODO: Verify there is such a code and if it is still valid
    if inserted_code == JoaoCode['code']:
        # Code becomes invalid after 1 minute of creation
        verificationDate = datetime.datetime.now()
        if verificationDate - JoaoCode["datetime"] > datetime.timedelta(minutes = 1):
            return {
                "valid": False, 
                "error": 0
            }
        else:
            try:
                r = requests.post(GATEDATASERVICE+"/API/gates/access", json={"gateID": gateID, "gateSecret": gateSecret,"success": True, "dateTime": str(verificationDate)} )
                # TODO: Missing post to user history
            except:
                return raise_error(7, "Couldn't Reach GateDataService")
            
            if r.status_code == 200:
                try:
                    error = r.json()["error"]
                except:
                    return raise_error(8, "Incorrect GateDataService response")

                if error == 0:
                    return {
                        "valid": True,
                        "error": 0
                    }
                elif error != 0:
                    try:
                        errorDescription = r.json()["errorDescription"]
                    except:
                        return raise_error(8, "Incorrect GateDataService response")
            
                    return raise_error(error, errorDescription)
            else:
                abort(r.status_code)
    else:
        return {
                "valid": False, 
                "error": 0
        }


# * Admin Web App Endpoints implementation

@app.route("/adminApp/WEB/createGate", methods=["GET","POST"])
def completeForm():
    if request.method == "GET":
        return render_template("createGate.html")
    elif request.method == "POST":
        result = request.form
        try:
            data = jsonify(result)
            aux = data.json
            aux['id'] = int(aux['id'])
            aux['secret'] = generate_code()
            dataJson = jsonify(aux)
        except: 
            return "Error: Inserted information not in the correct format."
        
        try: 
            r = requests.post(GATEDATASERVICE+ "/API/gates" , json=dataJson.json)
        except: 
            return "Server is down for the moment. Try again later."
        
        if r.status_code == 200:
            try:
                error = r.json()["error"]
            except:
                return "Error: Something went wrong in Server Response"
            
            if error == 0:
                try:
                    secret = r.json()["secret"]
                except:
                    return "Error: Something went wrong in Server Response"
                
                return render_template("newGate.html", message = secret )
            elif error > 0:
                try:
                    errorDescription = r.json()["errorDescription"]
                except:
                    return "Error: Something went wrong in Server Response"
                
                return "Error: " + errorDescription
        elif r.status_code == 400:
            return "Error: Inserted information not in the correct format"
        else:
            return "Error: Server not working correctly. Contact Admin"   
        
#listing of registered gates
# show a table with gates info (id, location, secret, activations)
@app.route("/adminApp/WEB/gates")
def allGatesAvailable():
    try:
        r = requests.get(GATEDATASERVICE+"/API/gates")
    except:
        return "Server is down for the moment. Try again later."

    if r.status_code == 200:
        try:
            error = r.json()["error"]
        except:
            return "Error: Something went wrong in Server Response"
        
        if error == 0:
            try:
                gatesList = r.json()["gatesList"]
            except:
                return "Error: Something went wrong in Server Response"

            return render_template("listGates.html", gatesInfo = gatesList)
        elif error > 0:
            try:
                errorDescription = r.json()["errorDescription"]
            except:
                return "Error: Something went wrong in Server Response"
            
            return "Error: " + errorDescription
    else:
        return "Error: Server not working correctly. Contact Admin"

# GET /adminApp/WEB/history - render page that shows a table with the 
# anonimized history of every attempt to open a gate
@app.route("/adminApp/WEB/history")
def accessHistoryAllGates():
    try:
        r = requests.get(GATEDATASERVICE+"/API/gates/history")
    except:
        return "Server is down for the moment. Try again later."

    if r.status_code == 200:
        try:
            error = r.json()["error"]
        except:
            return "Error: Something went wrong in Server Response"
        
        if error == 0:
            try:
                historyList = r.json()["historyList"]
            except:
                return "Error: Something went wrong in Server Response"
            print(historyList)
            return render_template("attemptsHistoryAllGates.html", historyInfo = historyList)
        elif error > 0:
            try:
                errorDescription = r.json()["errorDescription"]
            except:
                return "Error: Something went wrong in Server Response"
            
            return "Error: " + errorDescription
    else:
        return "Error: Server not working correctly. Contact Admin"

# GET /adminApp/WEB/history/<gateID> - render page that shows a table with the 
# anonimized history of every attempt to open a specific gate
@app.route("/adminApp/WEB/history/<path:gateID>")
def accessHistoryOfSomeGate(gateID):
    try:
        r = requests.get(GATEDATASERVICE+"/API/gates/{}/history".format(gateID))
    except:
        return "Server is down for the moment. Try again later."

    if r.status_code == 200:
        try:
            error = r.json()["error"]
        except:
            return "Error: Something went wrong in Server Response"
        
        if error == 0:
            try:
                historyList = r.json()["historyList"]
            except:
                return "Error: Something went wrong in Server Response"
            print(historyList)
            return render_template("attemptsHistoryOfSomeGate.html", gateID = gateID, historyInfo = historyList)
        elif error > 0:
            try:
                errorDescription = r.json()["errorDescription"]
            except:
                return "Error: Something went wrong in Server Response"
            
            return "Error: " + errorDescription
    else:
        return "Error: Server not working correctly. Contact Admin"


# Intermediary Version

# * Service Endpoints implementation

# for the UserApp to retrieve a new user code
@app.route("/API/users/<path:username>/code")
def getNewCode(username):
    if username != "joao":
        abort(404)

    # Invalidate last code if still valid
    code = generate_code()

    JoaoCode['code'] = code
    JoaoCode['datetime'] = datetime.datetime.now()

    return {
        "code": code, 
        "error": 0
    }
   
if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', port=8001, debug=True)
