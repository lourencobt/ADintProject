
# * Implement REST API to access, manipulate gate information in database
# * and implement additional operations

from flask import Flask, render_template, request, abort
from flask.json import jsonify

from gateDB import *

app = Flask(__name__)

# TODO: Endpoint 1: register new gate
    # URL: /gates/gateID or /gates/ # ! URL's need to be revised
    # ! Think about the possible errors

# TODO: Endpoint 2: get list of registered gates
    # URL: /gates/ -> # ! URL's need to be revised

    # ! Think about the possible errors

@app.route("/gates", methods=['GET', 'POST'])
def gates():
    if request.method == 'POST': #With the Post come one json like {"id": 10, "secret":"9999", "location":"EA1"}
        #parse body
        body = request.json

        # TODO: Verify if body is correct
        try:
            id = body['id']
            secret = body['secret']
            location = body['location']
        except KeyError:
            abort(400)

        # Register Gate
        if newGate(id, secret, location) == 0:
            return {"secret": secret}
        else:
            # ! Confirm if this is the appropriate error. 400 Bad Request
            # ! If the new data is in wrong format, should we inform the client??
            abort(400)
    elif request.method == 'GET':
        gates = listGates()
        gatesList = []
        for i in gates:
            gatesList.append({"id":i.id, "secret":i.secret, "location":i.location, "activations":i.activations})

        return jsonify(gatesList)
    else:
        # Never occurs this case, because of methods declare on app.route. However this is the intended error if 
        # for some reason the users enters this route with a wrong method
        # ! Confirm if this is needed
        abort(405)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)