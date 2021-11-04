
# * Implement REST API to access, manipulate gate information in database
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

from flask import Flask, request, abort
from flask.json import jsonify
import requests
from sqlalchemy.sql.expression import insert

from gateDB import *

GATEDATASERVICE = "http://localhost:8000"

app = Flask(__name__)

def raise_error(errorNumber, errorDescription):
    return {"error": errorNumber, "errorDescription":errorDescription}

# GET   /API/gates -> Register new gate
# POST  /API/gates -> List registered gates
@app.route("/API/gates", methods=['GET', 'POST'])
def gates():
    if request.method == 'POST': #With the Post come one json like {"id": 10, "secret":"9999", "location":"EA1"}
        #parse body
        body = request.json
        try:
            id = body['id']
            secret = body['secret']
            location = body['location']
        except:
            abort(400)

        # Register Gate
        if (error := newGate(id, secret, location)) == 0:
            return {
                "secret": secret, 
                "error": 0
            }
        elif error == -1:
            return raise_error(1,"Arguments to create a new gate are not in the correct format.")
        elif error == -2:
            return raise_error(2, "ID must be a positive integer.")
        elif error == -3:
            return raise_error(3, "Secret has not the correct secret length.")
        elif error == -4:
            return raise_error(4, "Location has to have a length bigger than 0.")
        elif error == -5:
            return raise_error(5, "There is already a gate with this ID.")
        else:
            return raise_error(100, "Something went wrong")
    elif request.method == 'GET':
        gates = listGates()
        gatesList = []
        for i in gates:
            gatesList.append({"id":i.id, "secret":i.secret, "location":i.location})

        return {
            "gatesList": gatesList,
            "error": 0
        }

# POST /API/gates/<gateID>/secret -> verify if posted secret of gate with id ID is valid
@app.route("/API/gates/<path:gateID>/secret", methods=['POST'])
def validateSecret(gateID):
    body = request.json
    try:
        secret = body["secret"]
    except:
        abort(400)

    #Verify there is such a code and if it is still valid
    if (error := secretOfGate(gateID)) == secret:
        return {
            "valid": True, 
            "error": 0
        }
    elif error == -1:
        return raise_error(6, "That is not a valid GateID")
    else: 
        return {
            "valid": False,
            "error":0
        }

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)