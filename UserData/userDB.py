
# * Implement database that will store every user information and history of all users

# Tablename = Users
# Columns:
#   - istID - String 
#   - name - String
#   - secret - String - It can be a String with 4 random characters
#   - secretUsed - Boolean 
#   - token - string 

# Tablename = History
# Columns:
#   - istID - String 
#   - gateID - Integer
#   - dateTime - dateTime

#%%
from datetime import datetime
import os

# sqlalchemy imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import except_
from sqlalchemy.sql.sqltypes import Boolean, Date, DateTime

SECRET_LEN = 4

DATABASE_FILE = "database.sqlite"

db_exists = False
if os.path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")


Base = declarative_base()

# Declaration of User Table
class users(Base):
    __tablename__ = 'Users'
    id = Column(String, primary_key=True)
    secret = Column(String)
    token = Column(String)
    valid = Column(Boolean)
    datesecret = Column(DateTime)
    def __repr__(self):
        return "<user(id = %s, secret = %s, token = %s, valid= %d, date secret= %s)>"%(
            self.id, self.secret, self.token, self.valid, str(self.datesecret))

# Declaration of History Table
class history(Base):
    __tablename__ = 'History'
    id = Column(Integer, primary_key=True)
    istID = Column(String)
    gateID = Column(Integer)
    date = Column(DateTime)
    def __repr__(self):
        return "<history( ID = %d, istID = %s, gateID = %d, date = %s)>" % (
            self.id, self.istID, self.gateID, str(self.date))


engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={"check_same_thread": False}) #echo = True shows all SQL calls
Session = sessionmaker(bind=engine)
session = Session() 
Base.metadata.create_all(engine)

#%%
#returns the list of the users
def listUsers():
    return session.query(users).all()
#returns the list of the history
def listHistory():
    return session.query(history).all()

#returns a user info
def userInfor(id):
        return session.query(users).filter(users.id == id).first()
#searches for the history of an unique user
def listUserHistory(istID):
        return session.query(history).filter(history.istID == istID).all()

#searches for information of an user
def listUsersId():
    return [i.id for i in session.query(users.id).all()]

#Creates a user
def newUser(id, token):
    # Verify if the type of the arguments is correct
    if type(id) != str or type(token) != str:
        return -1
    else: 
        user = users(id = id, token=token, valid = False)
        session.add(user)
        try:
            session.commit()
        except:
            session.rollback()
            return -2
        return 0

#Creates a new action (history) of an existent user
def newHistory(istID, gateID, date):
    # Verify if the type of the arguments is correct
    if type(istID) != str or type(gateID) != int or type(date) != datetime:
        return -1
    elif gateID < 1:
        return -2
    elif date > datetime.now():
        return -3
    else: 
        hist = history(istID = istID, gateID = gateID, date = date)
        session.add(hist)
        try:
            session.commit()
        except:
            session.rollback()
            return -4

        return 0

#Updates the token of an existent user 
def updateToken( id, token):
    
    user = session.query(users).filter(users.id == id).first()
    #check if there is any user with that id
    if not user:
        return -1
    #update token
    user.token = token
    try:
        session.commit()
    except:
        session.rollback()
        return -2

    return 0

#Updates the used token of an existent user 
def updateSecretUsed( id ):
    
    user = session.query(users).filter(users.id == id).first()
    #check if there is any user with that id
    if not user:
        return -1

    #update token
    user.valid = False 
    try:
        session.commit()
    except:
        session.rollback()
        return -2

    return 0

#Updates the secret an existent user
def updateSecret( id, secret ):
    # Verify if the secret has correct length. If not, this secret is not valid
    if len(secret) != SECRET_LEN:
        return -2

    user = session.query(users).filter(users.id == id).first()
    #check if there is any user with that id
    if not user:
        return -1
    #update secret
    user.secret = secret
    user.valid = True
    user.datesecret = datetime.now()
    try:
        session.commit()
    except:
        session.rollback()
        return -2

    return 0

# %%
