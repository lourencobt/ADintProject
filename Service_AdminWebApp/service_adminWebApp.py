
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

GATEDATASERVICE = "http://172.30.213.161:8000"
SECRET_LEN = 4
JoaoCode = {}

app = Flask(__name__)

# * Service Endpoints implementation
# * In this version, 2 endpoints

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

# for the UserApp to retrieve a new user code
@app.route("/API/users/<path:username>")
def getNewCode(username):
    if username != "joao":
        abort(404)

    # Invalidate last code if still valid
    code = generate_code()

    JoaoCode['code'] = code
    JoaoCode['datetime'] = datetime.datetime.now()

    return {"code": code}

# for the Gate to verify if a code is valid
@app.route("/API/code", methods=['POST'])
def verifyCode():
    data = request.json
    try:
        #Verify there is such a code and if it is still valid
        if JoaoCode["code"] == data["code"]:
            # Code becomes invalid after 1 minute of creation
            if datetime.datetime.now() - JoaoCode["datetime"] > datetime.timedelta(minutes = 1):
                return {"valid": False}
            else: 
                # ! Check this. Post?? We don't send nothing to post neither to put
                r = requests.post(GATEDATASERVICE+"/API/gates/{}/activation".format(data["gateID"]))
                if r.json()["success"]:
                    return {"valid": True}
                else:
                    abort(400)
        else: 
            return {"valid": False}
    except:
        abort(400)


# for the validation of a Gate 
@app.route("/API/gate", methods=['POST'])
def validateGate():
    data = request.json
    try:
        # Do request to the DB
        r = requests.post(GATEDATASERVICE+"/API/gates/{}/secret".format(data["gateID"]), json={"secret": data["gateSecret"]})
        # return validation
        return r.text
    except:
        abort(400)
        
@app.route("/admin/form")
def completeForm():
    return render_template("form.html")

@app.route("/admin/success", methods = ['POST'])
def wasSuccess():

    if request.method != 'POST':
        return render_template("400.html")

    else:

        result = request.form
        data = jsonify(result)
        aux = data.json
        aux['id'] = int(aux['id'])
        aux['secret'] = generate_code()
        inJson = jsonify(aux)
        
        requ = requests.post( "http://194.210.133.121:8000/gates" , json=inJson.json)

        if requ.status_code==200:
            return render_template("200.html")
        
        else:
            return render_template("400.html")

# # TODO: Page 2: listing of registered gates
#     # show a table with gates info (id, location, secret, activations)
#     # ! Think about the possible errors

@app.route("/admin/gates")
def allGatesAvailable():
# TODO: Request Code
    
    try:

        infoRequest = requests.get("http://194.210.133.121:8000/gates")

        print(infoRequest.json())

    except:
        # ! Should we do except to a especific exception?
        print("Request wasn't successful.")
        print("Exiting...")
        exit(-1)

    return render_template("allGates.html", gatesInfo = infoRequest.json())




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
