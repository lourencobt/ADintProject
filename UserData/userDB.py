
# * Implement database that will store every user information and history of all users

# Tablename = Users
# Columns:
#   - istID - String? 
#   - name - String
#   - secret - String - It can be a String with 4 random characters
#   - secretUsed ?? - Boolean 
#   - token ?? - string 

# Tablename = accessHistory ??
# Columns:
#   - istID - String? 
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
from sqlalchemy.sql.sqltypes import Date, DateTime

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
    def __repr__(self):
        return "<user(id = %s, secret = %s)>" % (self.id, self.secret)

# Declaration of History Table
class history(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    istID = Column(String)
    gateID = Column(Integer)
    date = Column(DateTime)
    def __repr__(self):
        return "<history( ID = %d, istID = %s, gateID = %d, date = %s)>" % (self.id, self.istID, self.gateID, str(self.date))


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

#searches for information of an user
def listUsersId():
    return [i.id for i in session.query(users.id).all()]

#searches for the history of an unique user
def listUserHistory(istID):
        return session.query(history).filter(history.istID == istID).all()


def newUser(id, secret):
    # Verify if the type of the arguments is correct
    if type(id) != str or type(secret) != str:
        return -1
    # Verify if the secret has correct length. If not, this secret is not valid
    elif len(secret) != SECRET_LEN:
        return -2
    else: 
        user = users(id = id, secret = secret)
        session.add(user)
        try:
            session.commit()
        except:
            session.rollback()
            return -3

        return 0

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


# %%
