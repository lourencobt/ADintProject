
# * Implement database that will store every gate information
# Tablename = Gates
# Columns:
#   - id - Integer - Primary Key
#   - location - String
#   - secret - String - It can be a String with 4 random characters
#   - activations - Integer -> Number of gate opens

import os

# sqlalchemy imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import except_

SECRET_LEN = 4

#SQL access layer initialization
DATABASE_FILE = "database.sqlite"
db_exists = False
if os.path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

Base = declarative_base()

# Declaration of Gates Table
class gates(Base):
    __tablename__ = 'Gates'
    id = Column(Integer, primary_key=True)
    secret = Column(String)
    location = Column(String)
    activations = Column(Integer)
    def __repr__(self):
        return "<Gates(id = %d, secret = %s, location = %s, activations = %d)>" % (self.id, self.secret, self.location, self.activations)
    
engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={"check_same_thread": False}) #echo = True shows all SQL calls
Session = sessionmaker(bind=engine)
session = Session() 
Base.metadata.create_all(engine)

def listGates():
    return session.query(gates).all()

def listGatesId():
    return [i.id for i in session.query(gates.id).all()]

def secretOfGate(id):
    try: 
        return session.query(gates).filter(gates.id == id).first().secret
    except:
        return -1

def activationOfGate(id):
    try:
        gateInfo = session.query(gates).filter(gates.id == id).first()
        gateInfo.activations = gateInfo.activations+1
    except:
        return -1
    
    try:
        session.commit()
    except:
        return -2
        
    return 0

        

def newGate(id, secret, location):
    # Verify if the type of the arguments is correct
    if type(id) != int or type(location) != str or type(secret) != str:
        return -1
    # Verify if Id is an Integer >= 1
    elif id < 1:
        return -2
    # Verify if the secret has correct length. If not, this secret is not valid
    elif len(secret) != SECRET_LEN:
        return -3
    # Verify if location length > 0.
    elif len(location) < 1:
        return -4
    else: 
        gate = gates(id = id, secret = secret, location = location, activations = 0)
        session.add(gate)
        try:
            session.commit()
        except:
            session.rollback()
            return -5

        return 0


