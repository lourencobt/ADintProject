
# * Intermediate Version of the project
# * This program has 2 purposes. It consist in the service + adminWebApp
# *     - Service:
# *         is composed of a set of REST endpoints that allow UserApp
# *         and GateApp to interact with the system
# *     - AdminWebApp:
# *         composed by two web pages, one for "Registration of a new gate" 
# *         and the other for "Listing registered gates"

# Imports

# * Service Endpoints implementation
# * In this version, 2 endpoints

# TODO: Endpoint 1: for the UserApp to retrieve a new user code
    # URL: /UserApp/users/joao # ! URL's need to be revised

    # ! Think about the possible errors

# TODO: Endpoint 2: for the Gate to verify if a code is valid
    # URL: /GateApp/ -> # ! URL's need to be revised

    # ! Think about the possible errors



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
