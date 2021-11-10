
# * Implementation of UserWebApp, GateWebApp and AdminWebApp

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
from requests_oauthlib import OAuth2Session
from flask import Flask, config, render_template, request, abort, redirect, session, url_for
from flask.json import jsonify
import json
import datetime 
import requests
from sqlalchemy.sql.functions import user
from flask_qrcode import QRcode

import sys
sys.path.insert(1, "../GateData")
from gateData import getGates, getHistoryofSomeGate

GATEDATASERVICE = "http://localhost:8000/"
USERDATASERVICE = "http://localhost:8002/"
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


def validate_session():
    # Verify if session token is still valid
    try:
        istID = session['istID']
    except:
        return "Error: You are not logged in"

    # Get user info to verify if user already exists
    try:
        r = requests.get(USERDATASERVICE + "API/users/{}".format(istID))
    except:
        return "Server is down for the moment. Try again later."

    if r.status_code == 200:
        try:
            error = r.json()["error"]
        except:
            return "Error: Something went wrong in Server Response"
        
        if error != 0:
            return  "Error: Something went wrong in Server Response"
    else:
        return "Error: Server not working correctly. Contact Admin"

    try:
        user_token = r.json()["userInfo"]["token"]
    except:
        return "Error: Something went wrong in Server Response"

    # if session token is valid
    if session['token'] == user_token:
        return True

#Information about my application in fenix
client_id = "570015174623415"
client_secret = "mE5JDJz+G53JEJBrYeSX2dD5YaMysnCqNykmvjd4mAWI3VuyGbnzSlgjIkCw36rn7ANvzYVy0YJ+4SNwJlUJxQ=="
authorization_base_url = 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog'
token_url = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token'

app = Flask(__name__)
QRcode(app)

# * User Web App Endpoints implementation
# WEB
@app.route("/userApp/WEB/login")
def authorization():
    #User Authorization.
    #Redirect the user/resource owner to the OAuth provider (i.e. fenix)
    #using an URL with a few key OAuth parameters.
    
    fenix = OAuth2Session(client_id, redirect_uri="http://localhost:8001/callback")
    authorization_url, state = fenix.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    session['admin'] = False
    return redirect(authorization_url)
  
@app.route("/userApp/WEB", methods=["GET"])
def homepage():
    try:
        istID = session['istID']
    except:
        return "Error: You are not logged in"
    return render_template("homePage.html" , username = istID)

@app.route("/userApp/WEB/QRCode", methods=["GET"])
def qrcodeRequest():
    
    try:
        istID = session['istID']
    except:
        return "Error: You are not logged in"

    # Verify if session token is still valid
    result = validate_session()

    if result == True:
        qrcode_data= {'istID': istID, 'secret': generate_code()}

        # Update secret to the most recent one
        # If successful render qrcode
        try:
            r = requests.post( USERDATASERVICE + "API/users/"+ istID +"/secret", json = qrcode_data)
        except:
            return "Server is down for the moment. Try again later."

        if r.status_code == 200:
            try:
                error = r.json()["error"]
            except:
                return "Error: Something went wrong in Server Response"
            
            if error == 0:
                return render_template("qrcode.html", code = json.dumps(qrcode_data))
            elif error != 0:
                "Error: Server not working correctly. Contact Admin"  
            else:
                return "Error: Server not working correctly. Contact Admin"  
        else:
            return "Error: Server not working correctly. Contact Admin"  
    else:
        return "Error: You need to be logged in."

@app.route("/userApp/WEB/history", methods=["GET"])
def userHistoryRequest():
    try:
        istID = session['istID']
    except:
        return "Error: You are not logged in"

    # Verify if session token is still valid
    result = validate_session()

    if result == True:
        # Get user history and render it
        try:
            r = requests.get( USERDATASERVICE + "API/users/"+ istID +"/history")
        except:
            return "Server is down for the moment. Try again later."

        if r.status_code == 200:
            try:
                error = r.json()["error"]
            except:
                return "Error: Something went wrong in Server Response"
            if error == 0:
                try:
                    history = r.json()["historyList"]
                except:
                    return "Error: Something went wrong in Server Response"
                
                return render_template("userHistory.html" , history = history )
            elif error != 0:
                return "Error: Server not working correctly. Contact Admin"  
        else:
            return "Error: Server not working correctly. Contact Admin"  
    else:
        return "Error: You need to be logged in."

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
    data = request.json
    
    try:
        istID = data["istID"]
        gateSecret = session["gateSecret"]
        inserted_code = data["secret"]
    except:
        abort(400)

    # First get user info to get the user secret
    try:
        r = requests.get(USERDATASERVICE + "API/users/{}".format(istID))
    except:
        return "Server is down for the moment. Try again later."

    if r.status_code == 200:
        try:
            error = r.json()["error"]
        except:
            return "Error: Something went wrong in Server Response"
        
        if error != 0:
            return  "Error: Something went wrong in Server Response"
    else:
        return "Error: Server not working correctly. Contact Admin"

    try:
        userInfo = r.json()["userInfo"]
    except:
        return "Error: Something went wrong in Server Response"

    if userInfo == None:
        return "Error: User not registered"
    
    verificationDate = datetime.datetime.now()
     # Verify there is such a code and if it is still valid
    if userInfo["valid"] == True and inserted_code == userInfo["secret"]:
        # Code becomes invalid after 1 minute of creation
        secretDate = datetime.datetime.fromisoformat(userInfo["dateSecret"])

        if verificationDate - secretDate > datetime.timedelta(minutes = 1):
            return {
                "valid": False, 
                "error": 0
            }
        else:
            # Post to gate history
            try:
                r = requests.post(GATEDATASERVICE+"API/gates/access", json={"gateID": gateID, "gateSecret": gateSecret,"success": True, "dateTime": str(verificationDate)} )
            except:
                return raise_error(7, "Couldn't Reach GateDataService")
            
            if r.status_code == 200:
                try:
                    error = r.json()["error"]
                except:
                    return raise_error(8, "Incorrect GateDataService response")

                if error != 0:
                    try:
                        errorDescription = r.json()["errorDescription"]
                    except:
                        return raise_error(8, "Incorrect GateDataService response")

                    return raise_error(error, errorDescription)

            # Post to User history
            try:
                r = requests.post(USERDATASERVICE+"API/users/access", json={"istID": istID, "gateID": gateID, "date": str(verificationDate)} )
            except:
                return raise_error(7, "Couldn't Reach UserDataService")
            
            if r.status_code == 200:
                try:
                    error = r.json()["error"]
                except:
                    return raise_error(8, "Incorrect UserDataService response")

                if error != 0:
                    try:
                        errorDescription = r.json()["errorDescription"]
                    except:
                        return raise_error(8, "Incorrect UserDataService response")
            
                    return raise_error(error, errorDescription)
            
            # Invalidate Secret
            try:
                r = requests.post(USERDATASERVICE+"API/users/{}/invalid".format(istID) )
            except:
                return raise_error(7, "Couldn't Reach UserDataService")
            
            if r.status_code == 200:
                try:
                    error = r.json()["error"]
                except:
                    return raise_error(8, "Incorrect UserDataService response")

                if error != 0:
                    try:
                        errorDescription = r.json()["errorDescription"]
                    except:
                        return raise_error(8, "Incorrect UserDataService response")
            
                    return raise_error(error, errorDescription)

            else:
                abort(r.status_code)
            
            return {
                        "valid": True,
                        "error": 0
                    }
    else:
        # Post to gate history
        try:
            r = requests.post(GATEDATASERVICE+"API/gates/access", json={"gateID": gateID, "gateSecret": gateSecret,"success": False, "dateTime": str(verificationDate)} )
        except:
            return raise_error(7, "Couldn't Reach GateDataService")
        
        if r.status_code == 200:
            try:
                error = r.json()["error"]
            except:
                return raise_error(8, "Incorrect GateDataService response")

            if error != 0:
                try:
                    errorDescription = r.json()["errorDescription"]
                except:
                    return raise_error(8, "Incorrect GateDataService response")
        
                return raise_error(error, errorDescription)
        else:
            abort(r.status_code)
            

        return {
                "valid": False, 
                "error": 0
        }


# * Admin Web App Endpoints implementation
@app.route("/adminApp/WEB/createGate", methods=["GET","POST"])
def completeForm():
    
    try:
        istID = session['istID']
    except:
        return "Error: You are not logged in"

    if session['admin']:
        if not isAdmin(istID):
            return "Error: you have no admin access!!!"
    
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
        istID = session['istID']
    except:
        return "Error: You are not logged in"

    if session['admin']:
        if not isAdmin(istID):
            return "Error: you have no admin access!!!"
    
    
    r = getGates()

    if r == -1:
        return "Error: Server not working correctly. Contact Admin"
    elif r.status_code == 200:
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
        istID = session['istID']
    except:
        return "Error: You are not logged in"

    if session['admin']:
        if not isAdmin(istID):
            return "Error: you have no admin access!!!"
    
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
        istID = session['istID']
    except:
        return "Error: You are not logged in"

    if session['admin']:
        if not isAdmin(istID):
            return "Error: you have no admin access!!!"

    r = getHistoryofSomeGate(gateID)

    if r == -1:
        return "Error: Server not working correctly. Contact Admin"

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
            return render_template("attemptsHistoryOfSomeGate.html", gateID = gateID, historyInfo = historyList)
        elif error > 0:
            try:
                errorDescription = r.json()["errorDescription"]
            except:
                return "Error: Something went wrong in Server Response"
            
            return "Error: " + errorDescription
    else:
        return "Error: Server not working correctly. Contact Admin"

@app.route("/adminApp/WEB/login")
def authorizationAdmin():
    #User Authorization.
    #Redirect the user/resource owner to the OAuth provider (i.e. fenix)
    #using an URL with a few key OAuth parameters.
    
    fenix = OAuth2Session(client_id, redirect_uri="http://localhost:8001/callback")
    authorization_url, state = fenix.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    session['admin'] = True
    return redirect(authorization_url)


#Call back must be the same to both apps 
@app.route("/callback")
def callback():
    
    # Step 3: Retrieving an access token.
    fenix = OAuth2Session(client_id, state=session['oauth_state'], 
        redirect_uri="http://localhost:8001/callback")
    
    token = fenix.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    session['oauth_token'] = token
    session['token'] = token['access_token']
    userinfo = fenix.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()
    session['istID'] = userinfo["username"]


    token = session['token']
    istID = session['istID']

    body = {"istID" : istID, "token" : token}

    # First get user info to verify if user already exists
    try:
        r = requests.get(USERDATASERVICE + "API/users/{}".format(istID))
    except:
        return "Server is down for the moment. Try again later."

    if r.status_code == 200:
        try:
            error = r.json()["error"]
        except:
            return "Error: Something went wrong in Server Response"
        
        if error != 0:
            return  "Error: Something went wrong in Server Response"
    else:
        return "Error: Server not working correctly. Contact Admin"

    # If user doesn't exist, create it
    if r.json()["userInfo"] == None:
        try:
            r = requests.post( USERDATASERVICE + "API/users", json = body)
        except:
            return "Server is down for the moment. Try again later."

        if r.status_code == 200:
            try:
                error = r.json()["error"]
            except:
                return "Error: Something went wrong in Server Response"
            if error == 0:
                return redirect("/userApp/WEB")
            else:
                return  "Error: Something happened with your account. Contact Admin"
        else:
            return "Error: Server not working correctly. Contact Admin"
    else: #If user already exist, actualize its information
        try:
            r = requests.post( USERDATASERVICE + "API/users/{}/token".format(istID), json ={"token": token})
        except:
            return "Server is down for the moment. Try again later."

        if r.status_code == 200:
            try:
                error = r.json()["error"]
            except:
                return "Error: Something went wrong in Server Response"
            if error != 0:
                return  "Error: Something went wrong in Server Response"
        else:
            return "Error: Server not working correctly. Contact Admin"
        
        if session['admin']:
            if isAdmin(istID):
                return redirect("/adminApp/WEB")
            else:
                return "Error: you have no admin access!!!"
                
        else:
            return redirect("/userApp/WEB")
   
@app.route("/adminApp/WEB", methods=["GET"])
def homepageadmin():

    try:
        istID = session['istID']
    except:
        return "Error: You are not logged in"

    if session['admin']:
        if isAdmin(istID):
            return render_template("homePageAdmin.html" , username = istID)
        else:
            return "Error: you have no admin access!!!"

def isAdmin(istID):
    
    #verify if ist in config.json
    with open('config.json') as f:
        data = json.load(f)
    
    admins = data['admins']
    
    for admin in admins:
        if admin == istID:
            return True
    
    return False

if __name__ == "__main__":

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', port=8001, debug=True)
