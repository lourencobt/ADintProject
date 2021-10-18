#%%
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

#%%
def listGates():
    return session.query(gates).all()

def listGatesId():
    return [i.id for i in session.query(gates.id).all()]

def newGate(id, secret, location):
    # Verify if there already a gate with id = id
    if id in listGatesId():
        return -1
    # Verify if the secret has correct length. If not, this secret is not valid
    elif len(secret) != SECRET_LEN:
        return -2
    # Verify if location length >= 2. We assume that a location has at least 2 characters
    elif len(location) < 2:
        return -3
    else:
        gate = gates(id = id, secret = secret, location = location, activations = 0)
        session.add()
        session.commit()
        return 0


