
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
from flask.json import jsonify

SECRET_LEN = 4

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

# TODO: Endpoint 1: for the UserApp to retrieve a new user code
    # URL: /UserApp/users/joao # ! URL's need to be revised

    # ! Think about the possible errors
@app.route("/users/joao")
def getNewCode():
    # Invalidate last code if still valid

    code = generate_code()
    return {"code": code}



# TODO: Endpoint 2: for the Gate to verify if a code is valid
    # URL: /GateApp/ -> # ! URL's need to be revised

    # ! Think about the possible errors
@app.route("GateApp", methods=['POST'])
def verifyCode():
    #Verify there is such a code
    #verify if it is still valid

# ! Don't Forget
# !     Every time the application is executed a new code is generated and retrieved
# !     Code becomes invalid after 1 minute of creation or when a new code is generated

# * AdminWebApp implementation
# * 2 pages

# TODO: Page 1: registration of a new gate
    # webpage with a form
    # Entries of the form
    #   gateID - unique identifier
    #   gateLocation - string 
    # 
    # If registration successful 
    #   show secret on admin browser
    # else:
    #   Show error

# TODO: Page 2: listing of registered gates
    # show a table with gates info (id, location, secret, activations)
    # ! Think about the possible errors
