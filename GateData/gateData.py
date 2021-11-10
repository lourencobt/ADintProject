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
