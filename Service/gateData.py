import requests

gateDataURL = ["http://localhost:8000", "http://localhost:7999"]
numberOfTolerance = len(gateDataURL)

def getGates():
    for i in range(numberOfTolerance):
        try:
            r = requests.get(gateDataURL[i]+"/API/gates")
        except:
            if i+1 != numberOfTolerance:
                continue;
            else:
                return -1
        return r

def getHistoryofSomeGate(gateID):
    for i in range(numberOfTolerance):
        try:
            r = requests.get(gateDataURL[i]+"/API/gates/{}/history".format(gateID))
        except:
            if i+1 != numberOfTolerance:
                continue;
            else:
                return -1
        return r

def getHistoryofAllGates():
    for i in range(numberOfTolerance):
        try:
            r = requests.get(gateDataURL[i]+"/API/gates/history")
        except:
            if i+1 != numberOfTolerance:
                continue;
            else:
                return -1
        return r

def postCreateGate(json):
    for i in range(numberOfTolerance):
        try: 
            r = requests.post(gateDataURL[i]+ "/API/gates", json=json)
        except: 
            if i+1 != numberOfTolerance:
                continue;
            else:
                return -1
    return r

def postVerifySecret(gateID, json):
    for i in range(numberOfTolerance):
        try: 
            r = requests.post(gateDataURL[i]+ "/API/gates/{}/secret".format(gateID), json=json)
        except: 
            if i+1 != numberOfTolerance:
                continue;
            else:
                return -1
    return r

def postGateHistory(json):
    for i in range(numberOfTolerance):
        try: 
            r = requests.post(gateDataURL[i]+ "/API/gates/access", json=json)
        except: 
            if i+1 != numberOfTolerance:
                continue;
            else:
                return -1
    return r
