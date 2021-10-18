
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
        id = body['id']
        secret = body['secret']
        location = body['location']

        # Register Gate
        if newGate(id, secret, location) == 0:
            return {"secret": secret}
        else:
            # TODO: Return appropriate error according to the return of newGate
            abort(404)
    elif request.method == 'GET':
        gatesData = listGates()
        return jsonify(gatesData)
    else:
        # TODO: Return appropriate error. In this case the HTTP method is wrong
        abort(404)


