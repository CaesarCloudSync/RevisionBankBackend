import base64
import concurrent
import os
from concurrent.futures import thread
from datetime import datetime
import datetime as dt
import requests
from bs4 import BeautifulSoup
from flask import Flask, app, jsonify, request
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message
from physicsaqa import PhysicsAQA
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from csv_to_db import ImportCSV
from models import Users 
from bson.objectid import ObjectId # 
import hashlib
import random
from datetime import datetime
from PIL import Image, ImageOps
from io import BytesIO
import base64
from websockets.exceptions import ConnectionClosedError
import json
import stripe
import jwt
#import cv2
from fastapi.responses import StreamingResponse
from fastapi import WebSocket,WebSocketDisconnect

import re
import jwt
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from typing import Generic, TypeVar,Dict,List,AnyStr,Any,Union
import asyncio 
import uvicorn
import pytesseract
from forgotpassemail import forgotpasswordemail
from RevisionBankModels import *
from fastapi_utils.tasks import repeat_every
from raspsendemail import RaspEmail
from revisionbankscheduler import RevisionBankScheduler
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
importcsv = ImportCSV("RevisionBankDB",maindb=0)
importcsvqp = ImportCSV("RevisionBankDB",maindb= 1)
importcsvqp1 = ImportCSV("RevisionBankQPs1",maindb=2)
revisionbankschedule = RevisionBankScheduler(importcsv)
JWT_SECRET = "Peter Piper picked a peck of pickled peppers, A peck of pickled peppers Peter Piper picked, If Peter Piper picked a peck of pickled peppers,Where's the peck of pickled peppers Peter Piper picked" #'super-secret'
# IRL we should NEVER hardcode the secret: it should be an evironment variable!!!
JWT_ALGORITHM = "HS256"

JSONObject = Dict[Any, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]
time_hour = (60 * 60) * 3 # 1 hour, * 3 hours
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
def getendsubscription(current_user):
    user_from_db = list(importcsv.db.users.find({"email": current_user}))[0]
    end_date = user_from_db["end_date_subscription"]
    return end_date
def provide_access_token(login_details,student=0):
    if student == 0:
        email_exists = list(importcsv.db.users.find({"email": login_details["email"]}))[0]
    elif student == 1:
        email_exists = list(importcsv.db.studentsubscriptions.find({"email": login_details["email"]}))[0]
    encrypted_password =  hashlib.sha256(login_details["password"].encode('utf-8')).hexdigest()
    if email_exists["password"] == encrypted_password:
        access_token = secure_encode({"email":email_exists["email"]}) #create_access_token(identity=email_exists["email"])
        return access_token
    else:
        return "Wrong password"
# Sending Emails from Heroku: https://blairconrad.com/2020/03/05/libraryhippo-2020-sending-email-from-heroku/
# Send Email API: https://app.sendgrid.com/
# Signin and Signup page: https://shayff.medium.com/building-your-first-flask-rest-api-with-mongodb-and-jwt-e03f2d317f04
# SetUp Tesseract: https://towardsdatascience.com/deploy-python-tesseract-ocr-on-heroku-bbcc39391a8d
def check_user_from_db(current_user): #test
    email_exists = importcsv.db.users.find_one({"email":current_user})
    student_email_exists = importcsv.db.studentsubscriptions.find_one({"email":current_user})
    if email_exists:
        user_from_db = list(importcsv.db.users.find({"email": current_user}))[0] # Gets wanted data for user
        return user_from_db
    elif student_email_exists:
        user_from_db = list(importcsv.db.studentsubscriptions.find({"email": current_user}))[0]
        return user_from_db


@app.get('/')# GET # allow all origins all methods.
async def index():
    return "Hello World"


@app.on_event("startup")
@repeat_every(seconds= time_hour * 1 ) # hours  # 24 hours 24
async def revisionbankschedulerevisioncardsrepeat() -> None:
    revisionbankschedule.runschedule()
    print("All Cards sent.")

@app.post("/revisionbanksendemail") # POST # allow all origins all methods.
async def revisionbanksendemail(data : JSONStructure = None):  
    try:
        data = dict(data)#request.get_json()
        try:
            attachment = data["attachment"]
        except KeyError as kex:
            attachment = None
        RaspEmail.send(**{"email":data["email"],"message":data["message"],"subject":data["subject"],"attachment":attachment})
        return {"message":"email has been sent."}
    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
@app.post("/revisionbankstripepayment") # POST # allow all origins all methods.
async def revisionbankstripepayment(data : JSONStructure = None, authorization: str = Header(None)):  
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            data = dict(data)#request.get_json()
            price = data["price"]
            stripe.api_key = "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"
            #"sk_test_51La4WnLpfbhhIhYRjP1w036wUwBoatAgqNRYEoj9u6jMd7GvSmBioKgmwJsabjgAY8V5W8i2r3QdelOPe5VNOueB00zDxeXtDQ"
            
            striperesponse = stripe.PaymentIntent.create(
            amount=round(price*100),
            currency="gbp",
            payment_method_types=["card"],
            )
            clientsecret= striperesponse["client_secret"]
            #print(clientsecret)
            return {"clientsecret":clientsecret}
        except Exception as ex:
            return {"error":f"{type(ex)}-{ex}"}

@app.post('/revisionbanktranslate') # POST # allow all origins all methods.
async def revisionbanktranslate(data : JSONStructure = None, authorization: str = Header(None)):   
    async def read_img(img):
        pytesseract.pytesseract.tesseract_cmd = "/app/.apt/usr/bin/tesseract"
        text = pytesseract.image_to_string(img,
                                            lang="eng",
                                            config='--dpi 300 --psm 6 --oem 2 -c tessedit_char_blacklist=][|~_}{=!#%&«§><:;—?¢°*@,')

        return(text)
    try:
        # TODO Use Tesseract OCR to get the text from the image hello
        data = dict(data)#request.get_json()
        img = data["revisioncardscreenshot"].replace("data:image/png;base64,","").replace("data:image/jpeg;base64,","")
        # TODO Next Remove Blurriness and Noise from the image with cv2
        #https://pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/
        img_obj  =ImageOps.grayscale(Image.open(BytesIO(base64.b64decode(img))))
        text = read_img(img_obj)

        return {"revisioncardscreenshotext":text }
        #return {"result":data}
    except Exception as e:
        return {f"error":f"{type(e)},{str(e)}"}


@app.post('/getedexcelqp') # POST # allow all origins all methods.
async def getedexcelqp(data : JSONStructure = None, authorization: str = Header(None)):   
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            data = dict(data)#request.get_json()
            edexcelpapers = list(importcsvqp.db.edexcelpapers.find({data["edexcelpaper"]:{"$exists":"true"}}))[0]
            del edexcelpapers["_id"]
            return {"edexcelpaper":edexcelpapers}
        except Exception as e:
            return {f"error":f"{type(e)},{str(e)}"}
@app.post('/getcomputerscienceqp') # POST # allow all origins all methods.
async def getcomputerscienceqp(data : JSONStructure = None, authorization: str = Header(None)):   
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            data = dict(data)#request.get_json()
            edexcelpapers = list(importcsvqp1.db.computerscienceqp.find({data["aqacomputerscience"]:{"$exists":"true"}}))[0]
            del edexcelpapers["_id"]
            return edexcelpapers # {"aqacomputerscience":edexcelpapers}
        except Exception as e:
            return {f"error":f"{type(e)},{str(e)}"}
@app.post('/getcomputersciencems') # POST # allow all origins all methods.
async def getcomputersciencems(data : JSONStructure = None, authorization: str = Header(None)):   
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            data = dict(data)#request.get_json()
            edexcelpapers = list(importcsvqp1.db.computersciencems.find({data["aqacomputerscience"]:{"$exists":"true"}}))[0]
            del edexcelpapers["_id"]
            return edexcelpapers # {"aqacomputerscience":edexcelpapers}
        except Exception as e:
            return {f"error":f"{type(e)},{str(e)}"}
@app.post('/getphysicsocrqp') # POST # allow all origins all methods.
async def getphysicsocrqp(data : JSONStructure = None, authorization: str = Header(None)):   
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            data = dict(data)#request.get_json()
            if data["subject"] == "physics":
                edexcelpapers = list(importcsvqp1.db.physicsocrqp.find({data["questionpapersubject"]:{"$exists":"true"}}))[0]
            elif data["subject"] == "chemistry":
                edexcelpapers = list(importcsvqp.db.chemistryaqaqp.find({data["questionpapersubject"]:{"$exists":"true"}}))[0]
            elif data["subject"] == "biology":
                edexcelpapers = list(importcsvqp.db.biologyaqaqp.find({data["questionpapersubject"]:{"$exists":"true"}}))[0]

            del edexcelpapers["_id"]
            #print(edexcelpapers)
            if data["scheme"] == "qp":
                return {"questionpapersubject":edexcelpapers[data["questionpapersubject"]]["questionpaper"]}
            elif data["scheme"] == "ms":
                return {"questionpapersubject":edexcelpapers[data["questionpapersubject"]]["markscheme"]}
        except Exception as e:
            return {f"error":f"{type(e)},{str(e)}"}


@app.post('/storeocrrevisioncards') # POST # allow all origins all methods.
async def storeocrrevisioncards(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            data_json = dict(data)#request.get_json() 
            print(data_json)
            data = data_json["revisioncardscheduler"]
            email_exists = importcsv.db.accountrevisioncards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists
                cards_not_exist = []
                user_revision_cards = list(importcsv.db.accountrevisioncards.find({"email": current_user}))[0] # Gets the email.
                
                #print(user_revision_cards)
                for card in data["revisioncards"]: # Checks if the revision card exists in the database.
                    if card not in user_revision_cards["revisioncards"]:
                            cards_not_exist.append(card) # If not, add it to the list.
                            #cards_that_exist.append(card)
                    if cards_not_exist != []:
                        new_cards = cards_not_exist + user_revision_cards["revisioncards"] # adds new cards to the list.
                        user_revision_cards["revisioncards"] = new_cards # Updates the list.
                        del user_revision_cards["_id"]
                        user_revision_cards["email"] = current_user # Sets the email to the current user.
                        #importcsv.db.accountrevisioncards.delete_many({"email":current_user}) # Allows data to be updated.
                        #importcsv.db.accountrevisioncards.insert_one(user_revision_cards) # Inserts the new data.
                        importcsv.db.accountrevisioncards.replace_one(
                        {"email":current_user},user_revision_cards
                    )
                        return {"message":"revision cards updated"}
                    elif cards_not_exist == []: # If the cards are already in the database, return a message.
                        return {"message":"No new cards"}

            elif not email_exists:
                return {"message": "account doesn't exist"}
        except Exception as ex:
            print(type(ex),ex)
@app.post('/storerevisioncards') # POST # allow all origins all methods.
async def storerevisioncards(data : JSONStructure = None, authorization: str = Header(None)):
    try:
        current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
        if current_user:
            data_json = dict(data)#request.get_json() # test
            data = data_json["revisioncardscheduler"]
            email_exists = importcsv.db.accountrevisioncards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists
                cards_not_exist = []
                user_revision_cards = list(importcsv.db.accountrevisioncards.find({"email": current_user}))[0] # Gets the email.
                
                #print(user_revision_cards)
                for card in data["revisioncards"]: # Checks if the revision card exists in the database.
                   if card not in user_revision_cards["revisioncards"]:
                        cards_not_exist.append(card) # If not, add it to the list.
                        #cards_that_exist.append(card)
                if cards_not_exist != []:
                    new_cards = cards_not_exist + user_revision_cards["revisioncards"] # adds new cards to the list.
                    user_revision_cards["revisioncards"] = new_cards # Updates the list.
                    del user_revision_cards["_id"]
                    user_revision_cards["email"] = current_user # Sets the email to the current user.
                    #importcsv.db.accountrevisioncards.delete_many({"email":current_user}) # Allows data to be updated.
                    #importcsv.db.accountrevisioncards.insert_one(user_revision_cards) # Inserts the new data.
                    importcsv.db.accountrevisioncards.replace_one(
                    {"email":current_user},user_revision_cards
                )
                    return {"message":"revision cards updated"}
                elif cards_not_exist == []: # If the cards are already in the database, return a message.
                    return {"message":"No new cards"}

            elif not email_exists:
                data["email"] = current_user
                importcsv.db.accountrevisioncards.insert_one(data)

                return {"message": "revision card stored"}
    except Exception as ex:
        print(type(ex),ex)
@app.put('/changesendtoemail')# PUT # allow all origins all methods.
async def changesendtoemail(data : JSONStructure = None, authorization: str = Header(None)): # TODO
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            email_exists = importcsv.db.accountrevisioncards.find_one({"email":current_user})
            if email_exists:
                scheduled_exists = importcsv.db.scheduledcards.find_one({"email":current_user})
                if scheduled_exists:
                    user_scheduled_cards = list(importcsv.db.scheduledcards.find({"email": current_user}))[0]
                    #importcsv.db.scheduledcards.delete_many(user_scheduled_cards)
                    del user_scheduled_cards["sendtoemail"]
                    sendtoemailscheduled = user_scheduled_cards["sendtoemail"]
                    user_scheduled_cards.update({"sendtoemail": sendtoemailscheduled})
                    #importcsv.db.scheduledcards.insert_one(user_scheduled_cards)
                    importcsv.db.scheduledcards.replace_one(
                    {"email":current_user},user_scheduled_cards
                )

                user_revision_cards = list(importcsv.db.accountrevisioncards.find({"email": current_user}))[0]
                #importcsv.db.accountrevisioncards.delete_many(user_revision_cards)
                del user_revision_cards["sendtoemail"]
                sendtoemail = data["sendtoemail"]
                user_revision_cards.update({"sendtoemail": sendtoemail})
                importcsv.db.accountrevisioncards.replace_one(
                {"email":current_user},user_revision_cards
                )
                #importcsv.db.accountrevisioncards.insert_one(user_revision_cards)
                return {"message": "Send to email changed."}
            elif not email_exists:
                return {"message":"email does not exist"}
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/changerevisioncard') # POST # allow all origins all methods.
async def changerevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            email_exists = importcsv.db.accountrevisioncards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists
                # TODO Slightly buggy here - removes old schedule from the database.
                scheduled_exists = importcsv.db.scheduledcards.find_one({"email":current_user})
                if scheduled_exists:
                    user_scheduled_cards = list(importcsv.db.scheduledcards.find({"email": current_user}))[0]
                    if user_scheduled_cards:
                        for card in user_scheduled_cards["revisioncards"]:
                            oldcard = {i:data[i] for i in data if i!='newrevisioncard'}

                            if card == oldcard:
                                user_scheduled_cards["revisioncards"].remove(card)
                        #importcsv.db.scheduledcards.delete_many({"email":current_user})
                        #importcsv.db.scheduledcards.insert_one(user_scheduled_cards)
                        importcsv.db.scheduledcards.replace_one(
                                    {"email":current_user},user_scheduled_cards
                                    )
                    

                user_revision_cards = list(importcsv.db.accountrevisioncards.find({"email": current_user}))[0]
                left_over_image = []
                for card in user_revision_cards["revisioncards"]:
                    oldcard = {i:data[i] for i in data if i!='newrevisioncard'}

                    oldcard["translation"] = card["translation"]    
                    oldcard["revisioncardimgname"] = card["revisioncardimgname"]    
                    oldcard["revisioncardimage"] = card["revisioncardimage"]     
                    if card == oldcard:
                        user_revision_cards["revisioncards"].remove(card)
                        left_over_image.append({"revisioncardimgname":card["revisioncardimgname"],"revisioncardimage":card["revisioncardimage"] })

                #print(user_revision_cards)
                del data["revisioncard"]
                data["translation"] = ""
                data["revisioncardimgname"] = left_over_image[0]["revisioncardimgname"]
                data["revisioncardimage"] = left_over_image[0]["revisioncardimage"]

                data["revisioncard"] = data["newrevisioncard"]
                del data["newrevisioncard"]
                user_revision_cards["revisioncards"].insert(0,data) # .append()
                #print(user_revision_cards)
                importcsv.db.accountrevisioncards.replace_one(
                                {"email":current_user},user_revision_cards
                                )
                #importcsv.db.accountrevisioncards.delete_many({"email":current_user})
                #importcsv.db.accountrevisioncards.insert_one(user_revision_cards)
                return {"message":"revision card changed."}
        except Exception as ex:
            #print({f"error":f"{type(ex)},{str(ex)}"})
            return {f"error":f"{type(ex)},{str(ex)}"}


            
@app.get('/getrevisioncards')# GET # allow all origins all methods.
async def getrevisioncards(authorization: str = Header(None)):
    def iter_df(user_revision_cards):
        for revisioncard in user_revision_cards["revisioncards"]:
            #print(revisioncard)
            revisioncard.update({"revisionscheduleinterval":revisioncard["revisionscheduleinterval"]})
            yield json.dumps(revisioncard)
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            email_exists = importcsv.db.accountrevisioncards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists
                user_revision_cards = list(importcsv.db.accountrevisioncards.find({"email": current_user}))[0]
                del user_revision_cards["_id"],user_revision_cards["email"]
                #return StreamingResponse(iter_df(user_revision_cards), media_type="application/json")
                return user_revision_cards
            elif not email_exists:
                return {"message":"No revision cards"} # Send in shape of data
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.websocket("/getrevisioncardsws")
async def getrevisioncardsws(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            
                authinfo = await websocket.receive_json()
                #print(authinfo)
                authorization = authinfo["headers"]["Authorization"]
                current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
                if current_user:
                    try:
                        email_exists = importcsv.db.accountrevisioncards.find_one({"email":current_user})
                        if email_exists:  # Checks if email exists
                            user_revision_cards = list(importcsv.db.accountrevisioncards.find({"email": current_user}))[0]
                            del user_revision_cards["_id"],user_revision_cards["email"]
                            #return StreamingResponse(iter_df(user_revision_cards), media_type="application/json")
                            #return user_revision_cards
                            for revisioncard in user_revision_cards["revisioncards"]:
                                revisioncard.update({"revisionscheduleinterval":user_revision_cards["revisionscheduleinterval"],"sendtoemail":user_revision_cards["sendtoemail"]})
                                await websocket.send_json(json.dumps(revisioncard)) # sends the buffer as bytes
                        elif not email_exists:
                            await websocket.send_json(json.dumps({"message":"No revision cards"}))
                            #return {"message":"No revision cards"} # Send in shape of data
                    except Exception as ex:
                        return {f"error":f"{type(ex)},{str(ex)}"}
                elif not current_user:
                    await websocket.send_json(json.dumps({"message":"No user."}))
    except ConnectionClosedError as cex:
        await websocket.send_json(json.dumps({"error":f"{type(cex)},{cex}"}))
    except WebSocketDisconnect as wex:
        pass





@app.post('/uploadrevisioncardtxtfile') # POST # allow all origins all methods.
async def uploadrevisioncardtxtfile(data : JSONStructure = None, authorization: str = Header(None)):
    try:
        current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
        if current_user:
            file = request.files["file"]
            if file:
                return {"message":file}
            elif not file:
                {"message":"No file"}
    except Exception as ex:
        return {f"error":f"{type(ex)},{str(ex)}"}


@app.post('/removerevisioncard') # POST # allow all origins all methods.
async def removerevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            email_exists = importcsv.db.accountrevisioncards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists
                # Remove the revision card from the database.
                user_revision_cards = list(importcsv.db.accountrevisioncards.find({"email": current_user}))[0]
                del data["sendtoemail"],data["revisionscheduleinterval"]
                for card in user_revision_cards["revisioncards"]:
                    #print(data)
                    if card == data:
                        user_revision_cards["revisioncards"].remove(card)
                #importcsv.db.accountrevisioncards.delete_many({"email":current_user})
                #importcsv.db.accountrevisioncards.insert_one(user_revision_cards)
                importcsv.db.accountrevisioncards.replace_one(
                    {"email":current_user},user_revision_cards
                )
                # Remove the revision card from the scheduled cards
                try:
                    user_scheduled_cards = list(importcsv.db.scheduledcards.find({"email": current_user}))[0]
                    for card in user_scheduled_cards["revisioncards"]:
                        if card == data:
                            user_scheduled_cards["revisioncards"].remove(card)
                    #importcsv.db.scheduledcards.delete_many({"email":current_user})
                    #importcsv.db.scheduledcards.insert_one(user_scheduled_cards)
                    importcsv.db.scheduledcards.replace_one(
                    {"email":current_user},user_scheduled_cards
                )
                    return {"message":"revision card removed"}
                except IndexError as iex:
                    return {"message":"revision card removed"}

        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/schedulerevisioncard') # POST # allow all origins all methods.
async def schedulerevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    try:
        current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
        if current_user:
            data = dict(data)#request.get_json() # test
            email_exists = importcsv.db.scheduledcards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists
                cards_not_exist = []
                user_scheduled_cards = list(importcsv.db.scheduledcards.find({"email": current_user}))[0] # Gets the email.
                
                #print(user_revision_cards)
                for card in data["revisioncards"]: # Checks if the revision card exists in the database.
                   if card not in user_scheduled_cards["revisioncards"]:
                        cards_not_exist.append(card) # If not, add it to the list.
                        #cards_that_exist.append(card)
                if cards_not_exist != []:
                    new_cards = cards_not_exist + user_scheduled_cards["revisioncards"] # adds new cards to the list.
                    user_scheduled_cards["revisioncards"] = new_cards # Updates the list.
                    del user_scheduled_cards["_id"]
                    user_scheduled_cards["email"] = current_user # Sets the email to the current user.
                    #importcsv.db.scheduledcards.delete_many({"email":current_user}) # Allows data to be updated.
                    #importcsv.db.scheduledcards.insert_one(user_scheduled_cards) # Inserts the new data.
                    importcsv.db.scheduledcards.replace_one(
                    {"email":current_user},user_scheduled_cards
                )
                    return {"message":"revision cards scheduled"}
                elif cards_not_exist == []: # If the cards are already in the database, return a message.
                    return {"message":"revision cards already scheduled"}

            elif not email_exists:
                data["email"] = current_user
                importcsv.db.scheduledcards.insert_one(data)

                return {"message": "revision card scheduled"}
    except Exception as ex:
        print(type(ex),ex)
@app.delete('/unscheduleallrevisioncard') # DELETE # allow all origins all methods.
async def unscheduleallrevisioncard(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            email_exists = importcsv.db.scheduledcards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists
                user_revision_cards = list(importcsv.db.scheduledcards.find({"email": current_user}))[0]
                user_revision_cards["revisioncards"] = []
                #importcsv.db.scheduledcards.delete_many({"email":current_user})
                #importcsv.db.scheduledcards.insert_one(user_revision_cards)
                importcsv.db.scheduledcards.replace_one(
                    {"email":current_user},user_revision_cards
                )
                return {"message":"Allrevision card unscheduled"}
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/unschedulerevisioncard') # POST # allow all origins all methods.
async def unschedulerevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            email_exists = importcsv.db.scheduledcards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists

                user_revision_cards = list(importcsv.db.scheduledcards.find({"email": current_user}))[0]
                for card in user_revision_cards["revisioncards"]:
                    if card == data:
                        user_revision_cards["revisioncards"].remove(card)
                #importcsv.db.scheduledcards.delete_many({"email":current_user})
                #importcsv.db.scheduledcards.insert_one(user_revision_cards)
                importcsv.db.scheduledcards.replace_one(
                    {"email":current_user},user_revision_cards
                )
                return {"message":"revision card unscheduled"}
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/sendnowrevisioncard') # POST # allow all origins all methods.
async def sendnowrevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    try:
        current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
        if current_user:
            data = dict(data)#request.get_json()
            now = datetime.now().strftime("%c")
            message = f"""{data['revisioncards'][0]['revisioncardtitle']}{data["revisioncards"][0]["revisioncard"]}"""
            #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":data["sendtoemail"],"message":message,"subject":f"{data['revisioncards'][0]['subject']} Send Now"}})
            RaspEmail.send(**{"email":data["sendtoemail"],"message":message,"subject":f"{data['revisioncards'][0]['subject']} Send Now"})
            #print(response.text)
            #msg = Message(f"{data['revisioncards'][0]['subject']} Send Now", recipients=[data["sendtoemail"]]) # "amari.lawal@gmail.com"
            #msg.body = f"Mail from RevisionCard Send Now at {now}"
            #if "!DOCTYPE" not in data["revisioncards"][0]["revisioncard"] or "h1" not in data["revisioncards"][0]["revisioncard"]:
            #    msg.html = f"""<pre>{data['revisioncards'][0]['revisioncardtitle']}
            #    {data["revisioncards"][0]["revisioncard"]}</pre>"""
            #elif "!DOCTYPE" in data["revisioncards"][0]["revisioncard"] or "h1" in data["revisioncards"][0]["revisioncard"]:
            #    msg.html = f"""
            #    {data['revisioncards'][0]['revisioncardtitle']}
            #    {data["revisioncards"][0]["revisioncard"]}
            #    """
            #print(msg)
            #mail.send(msg)
            return {"message":"revision card sent"}
    except Exception as ex:
        print({f"error":f"{type(ex)},{str(ex)}"})
        return {f"error":f"{type(ex)},{str(ex)}"}
@app.get('/checkschedulerevisioncard')# GET # allow all origins all methods.
async def checkschedulerevisioncard(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            email_exists = importcsv.db.scheduledcards.find_one({"email":current_user})
            if email_exists:  # Checks if email exists
                user_scheduled_cards = list(importcsv.db.scheduledcards.find({"email": current_user}))[0]
                del user_scheduled_cards["_id"],user_scheduled_cards["email"],user_scheduled_cards["revisionscheduleinterval"],user_scheduled_cards["sendtoemail"]
                return user_scheduled_cards
            elif not email_exists:
                return {"message":"revision cards not scheduled"} # Send in shape of data
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}

@app.post('/fmathsqp') # POST # allow all origins all methods.
async def fmathsqp(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        datajson = dict(data)#request.get_json()
        try:
            main_qp_url = "https://www.physicsandmathstutor.com/a-level-maths-papers/"
            data = datajson["furthermaths"] 
            email = data["email"]
            book_inp = data["furthermathsbook"]
            topic_inp = data["furthermathstopic"]
            platform = data["platform"]
            qp_sections = {"Core":["c1",'c2','c3','c4'],"Mechanics":['m1','m2','m3','m4','m5'],"Statistics":['s1','s2','s3','s4'],'Further Pure':['fp1','fp2','fp3'],'Decision Maths':['d1','d2']}
            if "c".lower() in book_inp.lower():
                book_choice = "c"
            elif "m".lower() in book_inp.lower():
                book_choice = "m"
            elif "s".lower() in book_inp.lower():
                book_choice = "s"
            elif "fp".lower() in book_inp.lower():
                book_choice = "fp"
            elif "d".lower() in book_inp.lower():
                book_choice = "d"
            elif "a".lower() in book_inp.lower():
                book_choice = "a"
            else:
                return {"result": "doesn't exist"}
            if book_choice != "a":
                endpoints = [endpoint for val in qp_sections.values() for endpoint in val if book_choice in endpoint]
            elif book_choice == "a":
                endpoints = [endpoint for val in qp_sections.values() for endpoint in val]
            
            
            pdf_result = []
            pdf_titles = []
            def qp_extraction(qp_url,end):
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0","Accept-Encoding": "gzip, async deflate", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
                response_topic = requests.get(f"{qp_url}/{end}-by-topic/",headers=headers).text
                #if "This site is currently under going scheduled maintenance." in response_topic:
                #    return {"error":"Physics maths tutor is in maintenance mode."}
                soup = BeautifulSoup(response_topic,features='lxml')
                for child in soup.find_all(['a'],href=True):
                    if topic_inp.lower() in str(child.text).lower():
                        pdf_url = child['href']
                        #print(pdf_url)
                        #print(f'{str(child.text).capitalize()}.pdf')
                        pdf_titles.append(f'{str(child.text).capitalize()}.pdf')
                        pdf_result.append(pdf_url)
                        #response = requests.get(pdf_url)
                        #pdf_result.append(str(response.content).replace("b'","").replace("'",""))

                        


        #print(endpoints)
            def topic_extraction(end):
                qp_extraction(main_qp_url,end)

            def threads_url(data : JSONStructure = None, authorization: str = Header(None)):
                #threads = 60 # 20 # TODO Number of threads may be blowing up the router.
                threads = 4
                with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor: #max_workers=threads
                    executor.map(topic_extraction,endpoints)
            threads_url()
            message = """
            The Further Maths question papers, email has been sent to you:
            """
            linkmessage = """
            The Further Maths question papers links:
            """

            #random.shuffle(pdf_result)
            #random.shuffle(pdf_titles)
            if pdf_result != []:
                if len(pdf_result) > 5:
                    pdf_slice = round(len(pdf_result) * (100/100))
                else:
                    pdf_slice = round(len(pdf_result) * (100/100))
                for link,title in zip(pdf_result[:pdf_slice],pdf_titles[:pdf_slice]):
                    linkmessage += "<br>"
                    linkmessage += f"{title}" + "<br>"
                    linkmessage += link.replace(" ",'%20') + "<br>"
                for i in pdf_titles:
                    message += "\n"
                    message += i + "\n"


                
                user_from_db = check_user_from_db(current_user)
                student_email_exists = importcsv.db.studentsubscriptions.find_one({"email":current_user})
                if "end_date_subscription" in user_from_db:
                    end_date = getendsubscription(current_user)
                    if user_from_db["emailsleft"] <= 0:
                        if platform == "app":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        elif platform == "web":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":0,"end_date_subscription":end_date}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        return pdf_response
                        
                    elif user_from_db["emailsleft"] > 0:
                        now = datetime.now().strftime("%c")
                        message = f"""
                        <h1>The Further Maths question papers links:</h1>
                        <p>{linkmessage}</p>.
                        """
                        #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":email,"message":message,"subject":"FMathqp PDFs"}})
                        RaspEmail.send(**{"email":email,"message":message,"subject":"FMathqp PDFs"})
            
                        #msg = Message("FMathqp PDFs", recipients=[email]) # "amari.lawal@gmail.com"
                        #msg.body = f"Mail from FMathqp at {now}"
                        #msg.html = f"""
                        #<h1>The Further Maths question papers links:</h1>
                        #<p>{linkmessage}</p>.
                        #"""
                        
                        #mail.send(msg)
                        user_from_db.update({"emailsleft":int(user_from_db["emailsleft"])-1})
                        importcsv.db.users.update_one({"email": current_user}, {"$set": user_from_db},upsert=True)
                        if platform == "app":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        elif platform == "web":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":int(user_from_db["emailsleft"])-1,"end_date_subscription":end_date}}
                        
                    return pdf_response
                elif "end_date_subscription" not in user_from_db and not student_email_exists:
                    if platform == "app":
                        pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                    elif platform == "web":
                        pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":0,"end_date_subscription":99999999}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                    return pdf_response
                elif "end_date_subscription" not in user_from_db and student_email_exists:
                    if user_from_db["emailsleft"] <= 0:
                        if platform == "app":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        elif platform == "web":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":0,"end_date_subscription":end_date}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        return pdf_response
                        
                    elif user_from_db["emailsleft"] > 0:
                        now = datetime.now().strftime("%c")
                        message = f"""
                        <h1>The Further Maths question papers links:</h1>
                        <p>{linkmessage}</p>.
                        """
                        #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":email,"message":message,"subject":"FMathqp PDFs"}})
                        RaspEmail.send(**{"email":email,"message":message,"subject":"FMathqp PDFs"})
                        user_from_db.update({"emailsleft":int(user_from_db["emailsleft"])-1})
                        importcsv.db.studentsubscriptions.update_one({"email": current_user}, {"$set": user_from_db},upsert=True)
                        if platform == "app":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        elif platform == "web":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":int(user_from_db["emailsleft"])-1,"end_date_subscription":99999999}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        return pdf_response
            elif pdf_result == []:
                return {"error":"No further maths question papers available"}
        except Exception as e:
            return {f"error":f"{type(e)},{str(e)}"}
    else:
        return {"message": "Login first please."}


@app.post('/fmathsb') # POST # allow all origins all methods.
async def fmathsb(data : JSONStructure = None, authorization: str = Header(None)):
    #pure maths: 0, statistics mechanics: 1, core pure maths: 2, further pure maths: 3, further statistics: 4, further mechanics: 5, decision maths: 6" 
    # year/book: 1, year/book: 2
    # {"furthermathsb":{"email":"amari.lawal@gmail.com","furthermathsbbook": 0,"furthermathsbyear":2}}
    # Output PureMaths Book 2
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            sb_books_list = {"0":"pure-maths","1":"statistics-mechanics","2":"core-pure-maths","3":"further-pure-maths","4":"further-statistics","5":"further-mechanics","6":"decision-maths"}
            datajson = dict(data)#request.get_json()
            data = datajson["furthermathsb"] 
            email = data["email"]
            sb_book_inp = str(data["furthermathsbbook"])
            sb_year_inp = str(data["furthermathsbyear"])
            sb_exercise = str(data["furthermathsbexercise"])
            platform = data["platform"]

            sb_book = sb_books_list[str(sb_book_inp)]
            sb_year = str(sb_year_inp)

            if sb_book == "pure-maths" or sb_book == "statistics-mechanics":
                sb_url = f"https://www.physicsandmathstutor.com/maths-revision/solutionbanks/edexcel-{sb_book}-year-{sb_year}/"
                #print(sb_url)
            else:
                sb_url = f"https://www.physicsandmathstutor.com/maths-revision/solutionbanks/edexcel-{sb_book}-{sb_year}/"
            
            book_dir_name = f"{sb_book}{str(sb_year)}".capitalize()
            
            response = requests.get(sb_url).text
            soup = BeautifulSoup(response,features='lxml')
            soup_a_tags = soup.find_all(['a'],href=True)
            sb_result = []
            sb_titles = []
            async def sb_extraction(child):
                if "Exercise" in child.text and sb_exercise.upper() in child.text:
                    print(child.text)
                    pdf_url = child['href']
                    #response = requests.get(pdf_url)
                    sb_titles.append(f'{book_dir_name}-{str(child.text).capitalize()}.pdf')
                    sb_result.append(pdf_url)
            async def threads_url(data : JSONStructure = None, authorization: str = Header(None)):
                #threads = 60 # 20 # TODO Number of threads may be blowing up the router.
                threads = 4
                with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor: #max_workers=threads
                    executor.map(sb_extraction,soup_a_tags)
            threads_url()
            if sb_result != []:
                message = """
                The Further Maths solution bank, email has been sent to you:
                """
                linkmessage = """
                The Further Maths question papers links:
                """
                for link,title in zip(sb_result,sb_titles):
                    linkmessage += "<br>"
                    linkmessage += f"{title}" + "<br>"
                    linkmessage += link.replace(" ",'%20') + "<br>"
                for i in sb_titles:
                    message += "\n"
                    message += i + "\n"
                user_from_db = check_user_from_db(current_user)
                student_email_exists = importcsv.db.studentsubscriptions.find_one({"email":current_user})
                if "end_date_subscription" in user_from_db:
                    end_date = getendsubscription(current_user)
                    if user_from_db["emailsleft"] <= 0:
                        if platform == "app":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        elif platform == "web":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":0,"end_date_subscription":end_date}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        return pdf_response
                    
                    elif user_from_db["emailsleft"] > 0:
                        now = datetime.now().strftime("%c")
                        message = f"""
                        <h1>The Further Maths Solution Bank links:</h1>
                        <p>{linkmessage}</p>.
                        """
                        #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":email,"message":message,"subject":"FMathSB PDFs"}})
                        RaspEmail.send(**{"email":email,"message":message,"subject":"FMathSB PDFs"})
                        #msg = Message("FMathSB PDFs", recipients=[email]) # "amari.lawal@gmail.com"
                        #msg.body = f"Mail from FMathsb at {now}"
                        #msg.html = f"""
                        #<h1>The Further Maths Solution Bank links:</h1>
                        #<p>{linkmessage}</p>.
                        #"""
                        
                        #mail.send(msg)
                        emailcount = int(user_from_db["emailsleft"])-1
                        user_from_db.update({"emailsleft":emailcount})
                        importcsv.db.users.update_one({"email": current_user}, {"$set": user_from_db},upsert=True)
                        
                        if platform == "app":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        elif platform == "web":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":emailcount,"end_date_subscription":end_date}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        return pdf_response
                elif "end_date_subscription" not in user_from_db and not student_email_exists:
                    if platform == "app":
                        pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                    elif platform == "web":
                        pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":0,"end_date_subscription":9999999}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                    return pdf_response
                elif "end_date_subscription" not in user_from_db and student_email_exists:
                    if user_from_db["emailsleft"] <= 0:
                        if platform == "app":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        elif platform == "web":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":0,"end_date_subscription":end_date}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        return pdf_response
                    
                    elif user_from_db["emailsleft"] > 0:
                        now = datetime.now().strftime("%c")
                        message = f"""
                        <h1>The Further Maths Solution Bank links:</h1>
                        <p>{linkmessage}</p>.
                        """
                        #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":email,"message":message,"subject":"FMathSB PDFs"}})
                        RaspEmail.send(**{"email":email,"message":message,"subject":"FMathSB PDFs"})
                        user_from_db.update({"emailsleft":int(user_from_db["emailsleft"])-1})
                        importcsv.db.studentsubscriptions.update_one({"email": current_user}, {"$set": user_from_db},upsert=True)
                        if platform == "app":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":message}} # "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        elif platform == "web":
                            pdf_response = {"furthermathsresult":{"furthermathsmessage":linkmessage,"emailcount":int(user_from_db["emailsleft"])-1,"end_date_subscription":9999999}}# "furthermathslinks":pdf_result,"furthermathstitles":pdf_titles,"furthermathslinkmessage":linkmessage
                        return pdf_response
            
            elif sb_result == []:
                return {f"error":f"No further maths solution bank for {sb_book} {sb_year}"}
        except Exception as e:
            return {f"error":f"{type(e)},{str(e)}"}
    else:
        return {"message": "Login first please."}
@app.post('/ocrsciencebookanswers') # POST # allow all origins all methods.
async def scienceocranswers(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        datajson = dict(data)#request.get_json()
        
        async def ocrscienceanswers(querydata):
            examboards = "OCR"
            url = "https://global.oup.com/education/content/secondary/series/ocr-a-level-sciences/a-level-sciences-for-ocr-student-book-answers/?region=uk"
            physicsanswerspdf = {}

            response= requests.get(url).text
            soup = BeautifulSoup(response,features='lxml')
            for divele in soup.find_all('div',{'class':'content_block half_width enclosed'}): # inner_block text_only_single ## 
                if querydata in divele.text:
                    for a in divele.find_all("a",href=True):
                        if a["href"] != "?region=uk":
                            physicsanswerspdf.update({a.text.replace("\xa0",' '): a["href"].replace("?region=uk",'')})

            result = {querydata:{examboards:physicsanswerspdf}}
            return result
        try:
            data = datajson["physicsocr"] 
            email = data["email"]
            subject = data["subject"] # physics, chemistry, biology
            physicsocralph =  data["physicsocralph"] # A or B
            chapter = data["chapter"] # Chapter 1
            year = data["year"] # AS/Year 1, A Level
            platform = data["platform"] # web or app

            query = f"{subject.capitalize()} {physicsocralph} {year}"
            papers = ocrscienceanswers(query)
            answerlink = papers[query]["OCR"][f"{chapter.capitalize()} (PDF)"].replace(" ",'%20')
            
            user_from_db = check_user_from_db(current_user)
            student_email_exists = importcsv.db.studentsubscriptions.find_one({"email":current_user})
            if "end_date_subscription" in user_from_db:
                end_date = getendsubscription(current_user)
                if user_from_db["emailsleft"] <= 0:
                    result = {"scienceocranswers": answerlink,"emailcount":0,"end_date_subscription":end_date}
                    return result
                elif user_from_db["emailsleft"] > 0:
                    now = datetime.now().strftime("%c")
                    message = f"""
                    <h1>OCR Science {query} Answers:</h1>
                    <p>{answerlink}</p>.
                    """
                    #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":email,"message":message,"subject":f"OCR {query} Answers"}})
                    RaspEmail.send(**{"email":email,"message":message,"subject":f"OCR {query} Answers"})
                    #msg = Message(f"OCR {query} Answers", recipients=[email]) # "amari.lawal@gmail.com"
                    #msg.body = f"Mail from {query} at {now}"
                    #msg.html = f"""
                    #<h1>OCR Science {query} Answers:</h1>
                    #<p>{answerlink}</p>.
                    #"""
                    
                    #mail.send(msg)
                    emailcount = int(user_from_db["emailsleft"])-1
                    user_from_db.update({"emailsleft":emailcount})
                    importcsv.db.users.update_one({"email": current_user}, {"$set": user_from_db},upsert=True)
                    result = {"scienceocranswers": answerlink,"emailcount":emailcount,"end_date_subscription":end_date}
                    return result
            elif "end_date_subscription" not in user_from_db and not student_email_exists:
                result = {"scienceocranswers": answerlink,"emailcount":0,"end_date_subscription":9999999}
                return result
            elif "end_date_subscription" not in user_from_db and student_email_exists:
                if user_from_db["emailsleft"] <= 0:
                    result = {"scienceocranswers": answerlink,"emailcount":0,"end_date_subscription":end_date}
                    return result
                elif user_from_db["emailsleft"] > 0:
                    now = datetime.now().strftime("%c")
                    message = f"""
                    <h1>OCR Science {query} Answers:</h1>
                    <p>{answerlink}</p>.
                    """
                    #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":email,"message":message,"subject":f"OCR {query} Answers"}})     
                    RaspEmail.send(**{"email":email,"message":message,"subject":f"OCR {query} Answers"})
                    user_from_db.update({"emailsleft":int(user_from_db["emailsleft"])-1})
                    importcsv.db.studentsubscriptions.update_one({"email": current_user}, {"$set": user_from_db},upsert=True)
                    result = {"scienceocranswers": answerlink,"emailcount":int(user_from_db["emailsleft"])-1,"end_date_subscription":9999999}
                    return result
        except Exception as e:
            return {f"error":f"{type(e)},{str(e)}"}
    else:
        return {"message": "Login first please."}
@app.post('/physicsaqa') # POST # allow all origins all methods.
async def physicsaqa(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            datajson = dict(data)#request.get_json()
            topicquestions =  PhysicsAQA().collectdata()
            data = datajson["physicsaqa"]
            email = data["email"]
            chapter = data["chapter"] # Section 1: Measurement & Their Errors
            topic = data["topic"] # Constituents of the Atom or The Law of the Atom
            platform = data["platform"] # web or app
            try:
                questionpaper = topicquestions[chapter][topic]
            except Exception as ex:
                return {"error":"chapter or topic not found"}
            try:
                markscheme = topicquestions[chapter][f"{topic} MS"]
            except Exception as ex:
                return {"error":"chapter or topic mark scheme not found"}
            
            
            user_from_db = check_user_from_db(current_user)
            student_email_exists = importcsv.db.studentsubscriptions.find_one({"email":current_user})
            if "end_date_subscription" in user_from_db:
                end_date = getendsubscription(current_user)
                if user_from_db["emailsleft"] <= 0:
                    return {"physicsaqa":{"chapter":chapter,"topic":topic,"question paper":questionpaper,"markscheme":markscheme,"emailcount":emailcount,"end_date_subscription":end_date}}
                elif user_from_db["emailsleft"] > 0:
                    now = datetime.now().strftime("%c")
                    message = f"""
                    <h1>PhysicsAqa Question Papers:</h1>
                    <p>{questionpaper}</p>
                    <p>{markscheme}</p>.
                    """
                    #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":email,"message":message,"subject":f"PhysicsAqa Papers"}})
                    RaspEmail.send(**{"email":email,"message":message,"subject":f"PhysicsAqa Papers"})
                    #msg = Message(f"PhysicsAqa Papers", recipients=[email]) # "amari.lawal@gmail.com"
                    #msg.body = f"Mail from physicsaqaApi at {now}"
                    #msg.html = f"""
                    #<h1>PhysicsAqa Question Papers:</h1>
                    #<p>{questionpaper}</p>
                    #<p>{markscheme}</p>.
                    #"""
                    #mail.send(msg)
                    emailcount = int(user_from_db["emailsleft"])-1
                    user_from_db.update({"emailsleft":emailcount})
                    importcsv.db.users.update_one({"email": current_user}, {"$set": user_from_db},upsert=True)
                    return {"physicsaqa":{"chapter":chapter,"topic":topic,"question paper":questionpaper,"markscheme":markscheme,"emailcount":emailcount,"end_date_subscription":end_date}}
            elif "end_date_subscription" not in user_from_db and not student_email_exists:
                return {"physicsaqa":{"chapter":chapter,"topic":topic,"question paper":questionpaper,"markscheme":markscheme,"emailcount":0,"end_date_subscription":9999999}}
            # If it is a student account
            elif "end_date_subscription" not in user_from_db and student_email_exists:
                # Check number of emails left
                if user_from_db["emailsleft"] <= 0:
                    return {"physicsaqa":{"chapter":chapter,"topic":topic,"question paper":questionpaper,"markscheme":markscheme,"emailcount":emailcount,"end_date_subscription":end_date}}
                elif user_from_db["emailsleft"] > 0:
                    now = datetime.now().strftime("%c")
                    message = f"""
                    <h1>PhysicsAqa Question Papers:</h1>
                    <p>{questionpaper}</p>
                    <p>{markscheme}</p>.
                    """
                    #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":email,"message":message,"subject":f"PhysicsAqa Papers"}})
                    RaspEmail.send(**{"email":email,"message":message,"subject":f"PhysicsAqa Papers"})
                    user_from_db.update({"emailsleft":int(user_from_db["emailsleft"])-1})
                    importcsv.db.studentsubscriptions.update_one({"email": current_user}, {"$set": user_from_db},upsert=True)
                    return {"physicsaqa":{"chapter":chapter,"topic":topic,"question paper":questionpaper,"markscheme":markscheme,"emailcount":int(user_from_db["emailsleft"])-1,"end_date_subscription":9999999}}
            
        except TypeError as tex:
            return {f"error":f"request is wrong shape {tex}"}
        except Exception as ex:
            return {f"error":f"{type(ex)} {str(ex)}"}
    else:
        return {"message": "Login first please."}


@app.post('/signupapi') # POST
async def signup(data: JSONStructure = None):
    try:
        signupdata = {}
        data = dict(data)
        hashed = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
        signupdata["email"] = data["email"]
        signupdata["password"] = hashed
        email_exists = importcsv.db.users.find_one({"email": signupdata["email"]})
        email_exists_student = importcsv.db.studentsubscriptions.find_one({"email": signupdata["email"]}) # Checks if student account exists
        if email_exists or email_exists_student:
            return {"message": "Email already exists"} # , 400
        elif not email_exists:
            # Notifies who are the beta testers
            #if datetime.now() < "2022-05-19T21:37:00.057084":
            #    signupdata.update({"betatest":"true"})
            importcsv.db.users.insert_one(signupdata)
            access_token = secure_encode({"email":signupdata["email"]})#create_access_token(identity=signupdata["email"])
            callback = {"status": "success","access_token":access_token}
            return callback
    except Exception as ex:
        error_detected = {"error": "error occured","errortype":type(ex), "error": str(ex)}
        return error_detected
@app.post('/loginapi') # POST
async def login(login_details: JSONStructure = None): # ,authorization: str = Header(None)
    # Login API
    try:



        login_details = dict(login_details)
        #print(login_details)
        email_exists = importcsv.db.users.find_one({"email": login_details["email"]})
        email_exists_student = importcsv.db.studentsubscriptions.find_one({"email": login_details["email"]}) # Checks if student account exists
        if email_exists:
            access_token = provide_access_token(login_details,student=0)
            if access_token == "Wrong password":
                return {"message": "The username or password is incorrect."}
            else:
                return {"access_token": access_token}
        elif email_exists_student:
            access_token = provide_access_token(login_details,student=1)
            if access_token == "Wrong password":
                return {"message": "The username or password is incorrect."}
            else:
                return {"access_token": access_token}
        return {"message": "The username or password is incorrect."}
    except Exception as ex:
        return {"error": f"{type(ex)} {str(ex)}"}
    #
@app.post('/forgotpassword') # POST
async def forgotpassword(data : JSONStructure = None):
    # Login API
    data = dict(data)#request.get_json()
    try:
        #print(data["email"])
        access_token = secure_encode({"email":data["email"]})#secure_decode(data["email"]) #create_access_token(identity=data["email"])
        # store token in database temporarily
        now = datetime.now().strftime("%c")
        #response = requests.post("http://0.0.0.0:7860/raspsendemail",json={"raspsendemail":{"email":data["email"],"message":forgotpasswordemail(data["email"],access_token),"subject":f"RevsionBank Password Reset"}})
        RaspEmail.send(**{"email":data["email"],"message":forgotpasswordemail(data["email"],access_token),"subject":f"RevsionBank Password Reset"})
        #msg = Message(f"RevsionBank Password Reset", recipients=[data["email"]]) # "amari.lawal@gmail.com"
        #msg.body = f"Mail from RevisionBank at {now}"
        #msg.html = forgotpasswordemail(data["email"],access_token)
        #mail.send(msg)
        return {"message": "Reset Email sent"}
    except Exception as ex:
        return {"error": f"{type(ex)} {str(ex)}"}

@app.put('/resetpassword') # PUT
async def resetpassword(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            email_exists = importcsv.db.users.find_one({"email": current_user})
            #print(email_exists)
            if email_exists:
                user_from_db = list(importcsv.db.users.find({"email": current_user}))[0]
                #print(user_from_db)
                # TODO Delete password from here and replace.
                #importcsv.db.users.delete_many(user_from_db)
                del user_from_db["password"]
                encrypted_password = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
                user_from_db.update({"password": encrypted_password})
                #importcsv.db.users.insert_one(user_from_db)
                importcsv.db.users.replace_one(
                    {"email":current_user},user_from_db
                )
                return {"message": "Password reset successful."}
            elif not email_exists:
                return {"message": "Email Doesn't exist."}
        except Exception as ex:
            return {"error": f"{type(ex)} {str(ex)}"}



@app.post('/storesubscription') # POST
async def storesubscription(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            data = dict(data)#request.get_json()
            user_from_db = list(importcsv.db.users.find({"email": current_user}))[0] # Gets wanted data for user
            if data["subscription"] == 'basic':
                emailsleft = {'emailsleft': 0}
            elif data["subscription"] == 'standard':
                emailsleft =  {'emailsleft': 40}
            elif data["subscription"] == 'premium' or data["subscription"] == 'educational':
                emailsleft =  {'emailsleft': 10000000000}
            if data["subscription"] == "educational":
                user_from_db.update({"numofaccounts": 200}) # TODO Constant Value needs to be changed when frontend is changed
            user_from_db.update({"start_date_subscription": data["start_date_subscription"]})
            user_from_db.update({"end_date_subscription": data["end_date_subscription"]})
            user_from_db.update({"subscription": data["subscription"]}) # Updates the user with the new subscription
            user_from_db.update(emailsleft)
            importcsv.db.users.update_one( { "email": current_user}, {"$set": user_from_db}, upsert = True )

            importcsv.db.subscriptionlog.insert_one({"email": user_from_db["email"],"start_date_subscription": data["start_date_subscription"], "end_date_subscription": data["end_date_subscription"], "subscription": data["subscription"], "emailsleft": emailsleft["emailsleft"]})
            return {"message": "Subscription Completed."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}

    else:
        return {"message": "User not found"}
@app.post('/storebetatester') # POST #
async def storebetatester(data : JSONStructure = None, authorization: str = Header(None)):
    data = dict(data)#request.get_json()
    emailsleft =  {'emailsleft': 10000000000}
    email_exists = importcsv.db.users.find_one({"email": data["email"]})
    if email_exists:
        user_from_db = list(importcsv.db.users.find({"email": data["email"]}))[0] # Gets wanted data for user
        #user_from_db.update({"numofaccounts": 200}) # TODO Constant Value needs to be changed when frontend is changed
        date_now = datetime.now()
        datetime_delta  = dt.timedelta(weeks=2)
        user_from_db.update({"start_date_subscription": date_now.isoformat()})
        
        user_from_db.update({"end_date_subscription": (datetime_delta + date_now).isoformat()})
        user_from_db.update({"subscription": "premium"}) # Updates the user with the new subscription
        user_from_db.update(emailsleft)
        user_from_db.update({"betatester": "true"})
        importcsv.db.users.update_one( { "email": data["email"]}, {"$set": user_from_db}, upsert = True )

        #importcsv.db.subscriptionlog.insert_one({"email": user_from_db["email"],"start_date_subscription": data["start_date_subscription"], "end_date_subscription": data["end_date_subscription"], "subscription": data["subscription"], "emailsleft": emailsleft["emailsleft"]})
        return {"message": "Beta Tester Subscription Completed."}
    elif not email_exists:
        return {"message": "User not found"}
@app.post('/storeeducationalfreetrial') # POST #
async def storeeducationalfreetrial(data : JSONStructure = None, authorization: str = Header(None)):
    data = dict(data)#request.get_json()
    try:
        emailsleft =  {'emailsleft': 10000000000}
        email_exists = importcsv.db.users.find_one({"email": data["email"]})
        if email_exists:
            user_from_db = list(importcsv.db.users.find({"email": data["email"]}))[0] # Gets wanted data for user
            #user_from_db.update({"numofaccounts": 200}) # TODO Constant Value needs to be changed when frontend is changed
            date_now = datetime.now()
            decimal_part = float(3 / 7)
            datetime_delta  = dt.timedelta(weeks=4 + decimal_part)
            user_from_db.update({"start_date_subscription": date_now.isoformat()})
            user_from_db.update({"numofaccounts": 200})
            
            user_from_db.update({"end_date_subscription": (datetime_delta + date_now).isoformat()})
            user_from_db.update({"subscription": "educational"}) # Updates the user with the new subscription
            user_from_db.update(emailsleft)
            importcsv.db.users.update_one( { "email": data["email"]}, {"$set": user_from_db}, upsert = True )

            #importcsv.db.subscriptionlog.insert_one({"email": user_from_db["email"],"start_date_subscription": data["start_date_subscription"], "end_date_subscription": data["end_date_subscription"], "subscription": data["subscription"], "emailsleft": emailsleft["emailsleft"]})
            return {"message": "Educational Freetrial Subscription Completed."}
        elif not email_exists:
            return {"message": "User not found"}
    except Exception as ex:
        return {"error": f"{type(ex)}-{ex}"}
@app.post('/scheduleeducationalfreetrial') # POST #
async def scheduleeducationalfreetrial(data : JSONStructure = None, authorization: str = Header(None)):
    data = dict(data)#request.get_json()
    try:
        regexdatetime = re.compile(r'\d\d\d\d-\d\d-\d\d')
        mo = regexdatetime.search(data["educationalfreetrialdate"])
        educationalfreetrialdate = mo.group()
    except AttributeError as aex:
        return {"error":r"Datetime shape is %Y-%m-%d"}
    try:
        email_exists = importcsv.db.users.find_one({"email": data["email"]})
        if email_exists:
            importcsv.db.schedulededucationalfreetrial.insert_one({"email": data["email"],"educationalfreetrialdate":educationalfreetrialdate})
            return {"message": "Educational Freetrial Scheduled."}
        elif not email_exists:
            return {"message": "User not found"}
    except Exception as ex:
        return {"error": f"{type(ex)}-{ex}"}
@app.post('/deletescheduleeducationalfreetrial') # POST #
async def deletescheduleeducationalfreetrial(data : JSONStructure = None, authorization: str = Header(None)):
    data = dict(data)#request.get_json()
    current_user = data["email"]
    current_user = importcsv.db.users.find_one({"email": data["email"]})
    if current_user:
        try:
            user_from_db = list(importcsv.db.schedulededucationalfreetrial.find({"email": data["email"]}))[0]
            importcsv.db.schedulededucationalfreetrial.delete_many(user_from_db)
            return {"message":"Educational Freetrial Unscheduled."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.post('/removebetatester') # POST #
async def removebetatester(data : JSONStructure = None, authorization: str = Header(None)):
    data = dict(data)#request.get_json()
    email_exists = importcsv.db.users.find_one({"email": data["email"]})
    if email_exists:
        user_from_db = list(importcsv.db.users.find({"email": data["email"]}))[0] # Gets wanted data for user
        importcsv.db.users.delete_many(user_from_db)
        del user_from_db["end_date_subscription"], user_from_db["start_date_subscription"],user_from_db["subscription"],user_from_db["emailsleft"], user_from_db["betatester"]
        importcsv.db.users.update_one( { "email": data["email"]}, {"$set": user_from_db}, upsert = True )
        return {"message": "Beta Tester Subscription Deleted."}
    elif not email_exists:
        return {"message": "User not found"}
@app.get('/getsubscription') # GET
async def getsubscription(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            user_from_db = list(importcsv.db.users.find({"email": current_user}))[0] # Gets wanted data for user
            end_date = user_from_db["end_date_subscription"]
            end_date_subscription = {"end_date_subscription": end_date}
            return end_date_subscription
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/getemailcount') # GET
async def getemailcount(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            user_from_db = list(importcsv.db.users.find({"email": current_user}))[0] # Gets wanted data for user
            emailcount = user_from_db["emailsleft"]
            emailcountres = {"emailcount": emailcount}
            return emailcountres
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.post('/storefreetrial') # POST
async def storefreetrial(data : JSONStructure = None, authorization: str = Header(None)): 
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try: 
            data = dict(data)#request.get_json()
            user_from_db = list(importcsv.db.users.find({"email": current_user}))[0] # Gets wanted data for user
            if 'freetrial' not in  user_from_db:
                user_from_db.update({"freetrial": "true"})
                emailsleft =  {'emailsleft': 10000000000}
                user_from_db.update({"start_date_subscription": data["start_date_subscription"]})
                user_from_db.update({"end_date_subscription": data["end_date_subscription"]})
                user_from_db.update({"subscription": data["subscription"]}) # Updates the user with the new subscription
                user_from_db.update(emailsleft)
                importcsv.db.users.update_one( { "email": current_user}, {"$set": user_from_db}, upsert = True )
                importcsv.db.users.update_one({"email": current_user}, {"$set": user_from_db}, upsert = True)
                importcsv.db.freetrialhistory.insert_one({"email": user_from_db["email"],"freetrial":"true"})
                return {"message": "Freetrial Redeemed."}
            elif 'freetrial' in user_from_db:
                return {"error": "Freetrial has already used."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.post('/setstudentsubscriptions') # POST
async def setstudentsubscriptions(data : JSONStructure = None, authorization: str = Header(None)): 
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        # Hostemail is the primary key for the studentsubscription collection
        try: 
            data = dict(data)#request.get_json() 
            # {"hostemail": "amari.lawal05@gmail.com","hostnumofaccounts": 198,"studentemails": [{"email": "6Lawala@truroschool.com","password": "mann35"},{"email": "Bola.lawal@hotmail.co.uk","password": "billy45"},{"email": "amari.lawal@gmail.com","password": "bobby46"}],"studentemailsleft": 20,"studentsubscription": "student educational"}
            user_from_db = list(importcsv.db.users.find({"email": current_user}))[0] # Host emails data
            studentsnotexist = []
            for student in data["studentemails"]: # data["studentemails"] is a list of dictionaries [{"email":"example@gmail.com","password":"password"},{"email":"example@gmail.com","password":"password"}]
                student_user_from_db = importcsv.db.studentsubscriptions.find_one({"email": student["email"]}) # Checks if any of the emails added are in the database
                if not student_user_from_db: # If the email is not in the database, then we need to store the data into the database
                    studentsnotexist.append(student) # Adds the email to the list of emails that do not exist in the database

            if studentsnotexist == []: # If all data is already in the database, no need to store it.
                return {"message": "all students exist."}
            elif studentsnotexist != []: # If there are emails that are not in the database, we need to store the data into the database
                if user_from_db["numofaccounts"] > 0:
                    for student in studentsnotexist: # Goes through the emails not in the database 
                        encrypted_password = hashlib.sha256(student["password"].encode('utf-8')).hexdigest()# Encrypts the password
                        # Then stores data into the studentsubscriptions collection
                        importcsv.db.studentsubscriptions.insert_one({"hostemail":current_user,"email": student["email"],"password": encrypted_password,"emailsleft": 20,"subscription": "student educational"})
                    
                    return {"message": "student subscriptions Set."}
                elif user_from_db["numofaccounts"] <= 0:
                    return {"error": "No more student accounts left."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/getstudentsubscriptions') # GET
async def getstudentsubscriptions(authorization: str = Header(None)): 
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try: 
            student_user_from_db = list(importcsv.db.studentsubscriptions.find({"hostemail": current_user})) # [0]
            user_from_db = list(importcsv.db.users.find({"email": current_user}))[0]
            for student in student_user_from_db:
                del student["_id"], student["password"],student["hostemail"],student['subscription']
            
            #importcsv.db.users.delete_many(user_from_db) # Deletes the data in order to update it.
            del user_from_db["numofaccounts"] # Deletes the numofaccounts to update it.
            user_from_db.update({"numofaccounts": 200 - len(student_user_from_db)}) # Updates the number of accounts
            #importcsv.db.users.insert_one(user_from_db) # inserts updated data into the host emails account
            importcsv.db.users.replace_one(
                    {"email":current_user},user_from_db
                )
            return {"result":student_user_from_db}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/checkstudentsubscriptions') # GET
async def checkstudentsubscriptions(authorization: str = Header(None)): 
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            student_from_db = list(importcsv.db.studentsubscriptions.find({"email": current_user}))[0] # Gets wanted data for user
            student_subscription  = student_from_db["subscription"]
            student_subscription_json = {"student_subscription": student_subscription}
            return student_subscription_json
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.post('/deletestudentaccount') # POST
async def deletestudentaccount(data : JSONStructure = None, authorization: str = Header(None)): 
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        data = dict(data)#request.get_json()
        try: 
            hostkey = importcsv.db.studentsubscriptions.find_one({"hostemail": current_user})
            studentkey = importcsv.db.studentsubscriptions.find_one({"email": data["studentemail"]})
            if hostkey and studentkey:
                importcsv.db.studentsubscriptions.delete_one({"email": data["studentemail"]})
                return {"message": "Student account deleted."}
            else:
                return {"error": "Student account does not exist."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.put('/changestudentpassword') # PUT
async def changestudentpassword(data : JSONStructure = None, authorization: str = Header(None)): 
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        data = dict(data)#request.get_json()
        try: 
            hostkey = importcsv.db.studentsubscriptions.find_one({"hostemail": current_user})
            studentkey = importcsv.db.studentsubscriptions.find_one({"email": data["studentemail"]})
            if hostkey and studentkey:
                student_user_from_db = list(importcsv.db.studentsubscriptions.find({"email": data["studentemail"]}))[0]
                # TODO Delete password from here and replace.
                #importcsv.db.studentsubscriptions.delete_many(student_user_from_db)
                del student_user_from_db["password"]
                encrypted_password = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
                student_user_from_db.update({"password": encrypted_password})
                importcsv.db.studentsubscriptions.replace_one(
                    {"email":current_user},student_user_from_db
                )
                #importcsv.db.studentsubscriptions.insert_one(student_user_from_db)
                return {"message": "Password reset successful."}
            else:
                return {"error": "Student account does not exist."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}



@app.get('/getfreetrial') # GET
async def getfreetrial(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try: 
            freetrialhistory = list(importcsv.db.freetrialhistory.find({"email": current_user}))[0] # Gets wanted data for user
            freetrial = freetrialhistory["freetrial"]
            freetrial_subscription = {"freetrial": freetrial} # check freetrial
            return freetrial_subscription
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/getemail') # GET
async def getemail(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try: 
            user_from_db = check_user_from_db(current_user)
            return {"email":user_from_db["email"]}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
    
@app.delete('/deletesubscription') # DELETE
async def deletesubscription(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            user_from_db = list(importcsv.db.users.find({"email": current_user}))[0]
            #importcsv.db.users.delete_many(user_from_db)
            if "end_date_subscription" in user_from_db:
                del user_from_db["end_date_subscription"]
            if "start_date_subscription" in user_from_db:
                del user_from_db["start_date_subscription"]
            if "subscription" in user_from_db:
                del user_from_db["subscription"]
            if "emailsleft" in user_from_db:
                del user_from_db["emailsleft"]
            if "numofaccounts" in user_from_db:
                del user_from_db["numofaccounts"]
            importcsv.db.users.replace_one(
                    {"email":current_user},user_from_db
                )
            #importcsv.db.users.update_one( { "email": current_user}, {"$set": user_from_db}, upsert = True )

            return {"message":"Subscription deleted from expiration"}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/getaccountinfo') # GET
async def getaccountinfo(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            email_exists = importcsv.db.users.find_one({"email": current_user})
            email_exists_student = importcsv.db.studentsubscriptions.find_one({"email": current_user})
            if email_exists:
                user_from_db = list(importcsv.db.users.find({"email": current_user}))[0]
                del user_from_db["password"], user_from_db["_id"]
                return user_from_db
            elif email_exists_student:
                student_user_from_db = list(importcsv.db.studentsubscriptions.find({"email": current_user}))[0]
                host_from_db = list(importcsv.db.users.find({"email": student_user_from_db["hostemail"]}))[0]
                student_user_from_db.update({"start_date_subscription":host_from_db["start_date_subscription"]})
                student_user_from_db.update({"end_date_subscription":host_from_db["end_date_subscription"]})
                del student_user_from_db["password"], student_user_from_db["_id"]
                return student_user_from_db
        #return {"error": f"account not found"}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.delete('/deleteaccount') # DELETE
async def deleteaccount(authorization: str = Header(None)):
    current_user = secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            user_from_db = list(importcsv.db.users.find({"email": current_user}))[0]
            importcsv.db.users.delete_many(user_from_db)
            return {"message":"Account Deleted"}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/getedexcelpapers')# GET # allow all origins all methods.
async def getedexcelpapers(authorization: str = Header(None)):
    try:
        data = dict(data)#request.get_json()
        dataedexcel = list(importcsv.db.edexcelpapers.find({"year":"AS Level"}))
        return {"result":dataedexcel}
    except Exception as ex:
        return {"error":f"{type(ex)},ex"}

async def main():
    config = uvicorn.Config("main:app", port=8000, log_level="info",host="0.0.0.0",reload=True)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())