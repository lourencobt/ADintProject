
# * Implement REST API to access, manipulate gate information in database
# * and implement additional operations

from flask import Flask, request, abort
from flask.json import jsonify

from gateDB import *

app = Flask(__name__)

# ! How can we do to only allow the service_adminWebApp to interact with some specific Endpoints?

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
        try:
            if newGate(id, secret, location) == 0:
                return {"secret": secret, "inserted": True}
            else:
                abort(400)
        except IntegrityError:
            session.rollback()
            return {"inserted": False}
    elif request.method == 'GET':
        gates = listGates()
        gatesList = []
        for i in gates:
            gatesList.append({"id":i.id, "secret":i.secret, "location":i.location, "activations":i.activations})

        return jsonify(gatesList)

# POST /API/gates/<gateID>/secret -> verify if posted secret of gate with id ID is valid
@app.route("/API/gates/<path:gateID>/secret", methods=['POST'])
def validateSecret(gateID):
    body = request.json
    try:
        #Verify there is such a code and if it is still valid
        if secretOfGate(gateID) == body["secret"]:
            return {"valid": True}
        else: 
            return {"valid": False}
    except:
        abort(400)

# POST /API/gates/<gateID>/activation -> Increment Activation of gate with id ID
@app.route("/API/gates/<path:gateID>/activation", methods=['POST'])
def changeActivation(gateID):
    # ! Need to prove that we know the gate secret
    try: 
        activationOfGate(gateID)
    except:
        return {"success": False}
    return {"success": True}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)