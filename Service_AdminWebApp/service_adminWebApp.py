
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

# Imports
from flask import Flask, render_template, request, abort
from flask import json
from flask.json import jsonify
import datetime 
import requests
from sqlalchemy import exc

GATEDATASERVICE = "http://localhost:8000/"
SECRET_LEN = 4
JoaoCode = {"code": "0"}

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

# for the Gate to verify if a code is valid
@app.route("/API/gates/<path:gateID>/code", methods=['POST'])
def verifyCode(gateID):
    data = request.json
    try:
        gateSecret = data["secret"]
        inserted_code = data["code"]
    except:
        abort(400)

    # Verify there is such a code and if it is still valid
    if JoaoCode["code"] == inserted_code:
        # Code becomes invalid after 1 minute of creation
        if datetime.datetime.now() - JoaoCode["datetime"] > datetime.timedelta(minutes = 1):
            return {
                "valid": False, 
                "error": 0
            }
        else: 
            try:
                r = requests.post(GATEDATASERVICE+"/API/gates/{}/activation".format(gateID), json={"secret": gateSecret} )
            except:
                return raise_error(7, "Couldn't Reach GateDataService")
            if r.status_code == 200:
                try:
                    error = r.json()["error"]
                except:
                    return raise_error(8, "Incorrect GateDataService response")

                if error == 0:
                    try:
                        success = r.json()["success"]
                    except:
                        return raise_error(8, "Incorrect GateDataService response")
                    
                    return {
                        "valid": success, 
                        "error": 0
                    }
                elif error > 0:
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

# for the validation of a Gate 
@app.route("/API/gate", methods=['POST'])
def validateGate():
    data = request.json
    try:
        gateID = data["gateID"]
        gateSecret = data["gateSecret"]
    except:
        abort(400)

    # Do request to the DB
    try:
        r = requests.post(GATEDATASERVICE+"/API/gates/{}/secret".format(gateID), json={"secret": gateSecret})
    except:
        return raise_error(7, "Couldn't Reach GateDataService")

    if r.status_code == 200:
        try:
            error = r.json()["error"]
        except:
            return raise_error(8, "Incorrect GateDataService response")
        
        if error == 0:
            try:
                valid = r.json()["valid"]
            except:
                return raise_error(8, "Incorrect GateDataService response")
            # return validation
            return {
                "valid": valid, 
                "error": 0
            }
        elif error > 0:
            try:
                errorDescription = r.json()["errorDescription"]
            except:
                return raise_error(8, "Incorrect GateDataService response")
            
            return raise_error(error, errorDescription)
    else:
        abort(r.status_code)
        
# * Admin Web App Endpoints implementation

@app.route("/admin/createGate")
def completeForm():
    return render_template("createGate.html")

@app.route("/admin/newGate", methods = ['POST'])
def wasSuccess():
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
@app.route("/admin/gates")
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
    else:
        return "Error: Server not working correctly. Contact Admin"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
