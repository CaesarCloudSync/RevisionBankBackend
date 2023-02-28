import jwt
from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import Optional
import asyncio 
import uvicorn
from RevisionBankModels import *
JWT_SECRET = "secret" # IRL we should NEVER hardcode the secret: it should be an evironment variable!!!
JWT_ALGORITHM = "HS256"

app = FastAPI()

class Auth(BaseModel):
    name: str
    password: str
class Person(BaseModel):
    name: str
    gender: Optional[str] = None
    age: float
    checked: Optional[bool] = None

@app.post("/signup")
async def root(person: Auth):
    try:
        person = dict(person)
        access_token = secure_encode({"name":person})
        print(access_token)
        # here we can add code to check the user (by email)
        # e.g. select the user from the DB and see its permissions
        return {"access_token":access_token}
    except Exception as ex:
        print(ex)
        return "Unauthorized Access!"
    # in this example we'll simply return the person entity from the request body
    # after adding a "checked"

@app.post("/signin")
async def root(person: Person, authorization: str = Header(None)):
    try:
        decoded = secure_decode(authorization.replace("Bearer ",""))
        # here we can add code to check the user (by email)
        # e.g. select the user from the DB and see its permissions
        print(decoded)
        return {"message":"signed in"}
    except:
        return "Unauthorized Access!"
    # in this example we'll simply return the person entity from the request body
    # after adding a "checked"

@app.post('/forgotpassword') # POST
def forgotpassword(data : GenericSingleObject):
    data = dict(data)
    print(data)
    return {"message":"hi"}

def secure_encode(token):
    # if we want to sign/encrypt the JSON object: {"hello": "world"}, we can do it as follows
    # encoded = jwt.encode({"hello": "world"}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    encoded_token = jwt.encode(token, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # this is often used on the client side to encode the user's email address or other properties
    return encoded_token

def secure_decode(token):
    # if we want to sign/encrypt the JSON object: {"hello": "world"}, we can do it as follows
    # encoded = jwt.encode({"hello": "world"}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
    # this is often used on the client side to encode the user's email address or other properties
    return decoded_token

async def main():
    config = uvicorn.Config("main:app", port=7860, log_level="info",host="0.0.0.0",reload=True)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())