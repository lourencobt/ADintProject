
# * Intermediate Version of the project
# * This program has 2 purposes. It consist in the service + adminWebApp
# *     - Service:
# *         is composed of a set of REST endpoints that allow UserApp
# *         and GateApp to interact with the system
# *     - AdminWebApp:
# *         composed by two web pages, one for "Registration of a new gate" 
# *         and the other for "Listing registered gates"

# Imports
from flask import Flask, render_template, request, abort
from flask import json
from flask.json import jsonify
import datetime 
import requests

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

    return {"code": code}

# for the Gate to verify if a code is valid
@app.route("/API/gates/<path:gateID>/code", methods=['POST'])
def verifyCode(gateID):
    data = request.json
    try:
        requested_code = data["code"]
    except:
        abort(400)

    # Verify there is such a code and if it is still valid
    if JoaoCode["code"] == requested_code:
        # Code becomes invalid after 1 minute of creation
        if datetime.datetime.now() - JoaoCode["datetime"] > datetime.timedelta(minutes = 1):
            return {"valid": False}
        else: 
            try:
                r = requests.post(GATEDATASERVICE+"/API/gates/{}/activation".format(gateID))
            except:
                # ! What to do when we cant contact the server? it is not a bad request
                abort(400)
            if r.status_code == 200:
                # ! verify error for example keyerror
                if r.json()["success"]:
                    return {"valid": True}
                else:
                    return {"valid": False}
            else:
                    # ! What to do when we cant contact the server? it is not a bad request
                abort(400)
    else: 
        return {"valid": False}

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
        # ! WHAT to do
        abort(400)
    
    if r.status_code == 200:
        # return validation
        return r.text
    # else:
    #     # !error

        

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
        
        try:
            if r.status_code == 200:
                if r.json()["inserted"]:
                    return render_template("newGate.html", message = r.json()["secret"] )
                else:
                    return "Error: There are already one gate with that ID."
            elif r.status_code == 400:
                return "Error: Inserted information not in the correct format."
            else:
                return "Error: Server not working correctly. Contact Admin"
            
        except: 
            return "Error: Something went wrong in Server Response"
        

#listing of registered gates
# show a table with gates info (id, location, secret, activations)
@app.route("/admin/gates")
def allGatesAvailable():
    try:
        infoRequest = requests.get(GATEDATASERVICE+"/API/gates")
    except:
        return "Server is down for the moment. Try again later."

    if infoRequest.status_code == 200:
        return render_template("listGates.html", gatesInfo = infoRequest.json())
    else:
        return "Error: Server not working correctly. Contact Admin"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
