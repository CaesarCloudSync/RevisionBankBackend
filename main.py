import os
import json
import base64
import hashlib
import asyncio 
import uvicorn
import requests
from dotenv import load_dotenv
from csv_to_db import ImportCSV# 
from fastapi import FastAPI, Header
from typing import Dict,List,Any,Union
from CaesarSQLDB.caesarcrud import CaesarCRUD
from CaesarSQLDB.caesarhash import CaesarHash
from fastapi.responses import StreamingResponse
from fastapi import WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from CaesarAICronEmail.CaesarAIEmail import CaesarAIEmail
from RevisionBankJWT.revisionbankjwt import RevisionBankJWT
from RevisionBankExceptions.revisionbankexceptions import *
from RevisionBankCron.revisionbankcron import RevisionBankCron
from CaesarSQLDB.caesar_create_tables import CaesarCreateTables
from RevisionBankUtils.revisionbankutils import RevisionBankUtils

from RevisionBankSQLOps.revisionbanksqlops import RevisionBankSQLOps

load_dotenv(".env")
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
revisionbankutils = RevisionBankUtils(importcsv)

caesarcrud = CaesarCRUD()
revisionbankjwt = RevisionBankJWT(caesarcrud)
caesarcreatetables = CaesarCreateTables()
caesarcreatetables.create(caesarcrud)
revisionbankcron = RevisionBankCron()
revsqlops = RevisionBankSQLOps(caesarcrud,caesarcreatetables)
qstash_access_token = base64.b64decode(os.environ.get("QSTASH_ACCESS_TOKEN").encode()).decode()
JSONObject = Dict[Any, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]
time_hour = (60 * 60) * 3 # 1 hour, * 3 hours

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await manager.broadcast(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)
manager = ConnectionManager()

@app.get('/')# GET # allow all origins all methods.
async def index():
    return "Hello World"
@app.post('/signupapi') # POST
async def signup(data: JSONStructure = None):
    try:
        signupdata = {}
        data = dict(data)
        hashed = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
        signupdata["email"] = data["email"]
        signupdata["password"] = hashed
        table = "users"
        condition = f"email = '{signupdata['email']}'"
        email_exists = caesarcrud.check_exists(("*"),"users",condition=condition)
        email_exists_student = caesarcrud.check_exists(("*"),"studentsubscriptions",condition=condition)
        if email_exists or email_exists_student:
            return {"message": "Email already exists"} # , 400
        elif not email_exists:

            res = caesarcrud.post_data(("email","password"),(signupdata["email"],signupdata["password"]),table=table)
            if res:
                access_token = revisionbankjwt.secure_encode({"email":signupdata["email"]})#create_access_token(identity=signupdata["email"])
                callback = {"status": "success","access_token":access_token}
            else:
                return {"error":"error when posting signup data."}
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
        condition = f"email = '{login_details['email']}'"
        email_exists = caesarcrud.check_exists(("*"),"users",condition=condition)
        email_exists_student = caesarcrud.check_exists(("*"),"studentsubscriptions",condition=condition)
        if email_exists:
            access_token = revisionbankjwt.provide_access_token(login_details,student=0)
            if access_token == "Wrong password":
                return {"message": "The username or password is incorrect."}
            else:
                return {"access_token": access_token}
        elif email_exists_student:
            access_token =  revisionbankjwt.provide_access_token(login_details,student=1)
            if access_token == "Wrong password":
                return {"message": "The username or password is incorrect."}
            else:
                return {"access_token": access_token}
        return {"message": "The username or password is incorrect."}
    except Exception as ex:
        return {"error": f"{type(ex)} {str(ex)}"}

@app.post('/storerevisioncards') # POST # allow all origins all methods.
async def storerevisioncards(data : JSONStructure = None, authorization: str = Header(None)):
    try:
        current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
        if current_user:
            data_json = dict(data)#request.get_json() # tes
            data = data_json["revisioncardscheduler"]
            sendtoemail = data["sendtoemail"]
            for revisioncard in data["revisioncards"]:
                revisioncard = {"subject":revisioncard["subject"],"sendtoemail":sendtoemail,"revisioncardtitle":revisioncard["revisioncardtitle"],"revisionscheduleinterval":revisioncard["revisionscheduleinterval"],"revisioncard":revisioncard["revisioncard"],"revisioncardimgname":revisioncard["revisioncardimgname"],"revisioncardimage":revisioncard["revisioncardimage"]}
                revisioncardhash = CaesarHash.hash_text(current_user + revisioncard["subject"]  + revisioncard["revisioncardtitle"])
                email_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.accountrevisioncards_table,condition=f"revisioncardhash = '{revisioncardhash}'")

                if not email_exists:
                    res = revsqlops.store_revisoncard(revisioncard,revisioncardhash,current_user,caesarcreatetables.accountrevisioncards_table)
                                                #res = caesarcrud.update_data(("revisioncardimgname",),
                            #    (revisioncardimgname,),caesarcreatetables.accountrevisioncards_table,f"revisioncardhash = '{revisioncardhash}'")   
                    if res:
                        for ind,revisioncardimgname in enumerate(revisioncard["revisioncardimgname"]): 
                            revisioncardimage = revisioncard["revisioncardimage"][ind]
                            if ind == 0:
                                res = caesarcrud.update_data(("revisioncardimgname",),
                                    ("true",),caesarcreatetables.accountrevisioncards_table,f"revisioncardhash = '{revisioncardhash}'")    
                            resblob = revsqlops.store_revisoncard_image(current_user,revisioncardimgname,revisioncardimage,revisioncardhash)
                            if resblob:
                                pass
                            else:
                                raise BLOBPostException("There was an error when posting with BLOB SQL.")          
                    else:
                        raise PostException("There was an error when posting with SQL.")

                else:
                    pass
            return {"message": "revision card stored"}
    except Exception as ex:
        print(type(ex),ex)
        return {"error":f"{type(ex)},{ex}"}
@app.post('/changerevisioncard') # POST # allow all origins all methods.
async def changerevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    try:
        current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
        if current_user:
            data = dict(data)#request.get_json() # tes
            revisioncard = {
                        "revisioncard": data["revisioncard"],
                        "newrevisioncard": data["newrevisioncard"],
                        "revisioncardtitle": data["revisioncardtitle"],
                        "subject": data["subject"],
                        "revisionscheduleinterval": data["revisionscheduleinterval"]
                    }   
            revisioncardhash = CaesarHash.hash_text(current_user + revisioncard["subject"]  + revisioncard["revisioncardtitle"])
            
            condition = f"revisioncardhash = '{revisioncardhash}'"
            schedule_exists = caesarcrud.check_exists(("*"),caesarcreatetables.schedule_table,condition=condition)
            if schedule_exists:
                revsqlops.unschedule_card_qstash(condition)
            res = caesarcrud.update_data(("revisioncard",),(revisioncard["newrevisioncard"],),caesarcreatetables.accountrevisioncards_table,condition=f"revisioncardhash = '{revisioncardhash}'")
            if res:
                return {"message":"revision card changed."}
            else:
                return {"error":"error when updating"}
    except Exception as ex:
        print(type(ex),ex)
        return {"error":f"{type(ex)},{ex}"}
@app.post('/changerevisioncardmetadata') # POST # allow all origins all methods.
async def changerevisioncardmetadata(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            oldcard_data = {"oldsubject":data["oldsubject"],"oldrevisioncardtitle":data["oldrevisioncardtitle"],"oldrevisionscheduleinterval":data["oldrevisionscheduleinterval"]}
            newcard_data = {"subject":data["newsubject"],"revisioncardtitle":data["newrevisioncardtitle"],"revisionscheduleinterval": data["newrevisionscheduleinterval"]}

        
            revisioncardhash = CaesarHash.hash_text(current_user + oldcard_data["oldsubject"]  + oldcard_data["oldrevisioncardtitle"])
            newrevisioncardhash = CaesarHash.hash_text(current_user + newcard_data["subject"]  + newcard_data["revisioncardtitle"])
            
            condition = f"revisioncardhash = '{revisioncardhash}'"
            # TODO Slightly buggy here - removes old schedule from the database.
            schedule_exists = caesarcrud.check_exists(("*"),caesarcreatetables.schedule_table,condition=condition)
            if schedule_exists:
                revsqlops.unschedule_card_qstash(condition)

            res = caesarcrud.update_data(("subject","revisioncardtitle","revisionscheduleinterval","revisioncardhash"),
                                   (newcard_data["subject"],newcard_data["revisioncardtitle"],newcard_data["revisionscheduleinterval"],newrevisioncardhash),
                                   caesarcreatetables.accountrevisioncards_table,condition=condition)
            res = caesarcrud.update_data(("revisioncardhash",),
                        (newrevisioncardhash,),
                        caesarcreatetables.revisioncardimage_table,condition=condition)
            if res:
                return {"message":"revision card meta data changed."}
            else:
                return {"error":"error when updating metadata."}

        except Exception as ex:
            #print({f"error":f"{type(ex)},{str(ex)}"})
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.put('/changesendtoemail') # POST # allow all origins all methods.
async def changesendtoemail(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            sendtoemail_data = {"sendtoemail":data["sendtoemail"]}
            condition = f"email= '{current_user}'"
            res = caesarcrud.update_data(("sendtoemail",),(sendtoemail_data["sendtoemail"],),caesarcreatetables.accountrevisioncards_table,condition=condition)
            if res:
                return {"message": "Send to email changed."}
            else:
                return {"error":"error when updating data"}
        except Exception as ex:
            #print({f"error":f"{type(ex)},{str(ex)}"})
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.get('/getaccountinfo') # GET
async def getaccountinfo(authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            condition = f"email = '{current_user}'"
            email_exists = caesarcrud.check_exists(("*"),"users",condition=condition)
            email_exists_student = caesarcrud.check_exists(("*"),"studentsubscriptions",condition=condition)
            if email_exists:
                #user_from_db = list(importcsv.db.users.find({"email": current_user}))[0]
                email_data = caesarcrud.get_data(("email",),"users",condition=condition)[0]
                return email_data 
            elif email_exists_student:
                pass
                #email_data = caesarcrud.get_data(("email"),"studentsubscriptions",condition=condition)[0]
                #student_user_from_db = list(importcsv.db.studentsubscriptions.find({"email": current_user}))[0]
                #host_from_db = list(importcsv.db.users.find({"email": student_user_from_db["hostemail"]}))[0]
                #student_user_from_db.update({"start_date_subscription":host_from_db["start_date_subscription"]})
                #student_user_from_db.update({"end_date_subscription":host_from_db["end_date_subscription"]})
                #del student_user_from_db["password"], student_user_from_db["_id"]
                #return student_user_from_db
        #return {"error": f"account not found"}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
import re

def is_hexadecimal(input_bytes):
    # Define a regular expression pattern for a valid hexadecimal string
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    
    # Convert the bytes to a string (assuming it's in ASCII encoding)
    hex_string = input_bytes.decode('ascii')
    
    # Use the regular expression to check if it's a valid hexadecimal
    return bool(hex_pattern.match(hex_string))

# Example usage:

@app.websocket("/getrevisioncardsws/{client_id}")
async def getrevisioncardsws(websocket: WebSocket,client_id:str):
    await manager.connect(websocket)
    try:
        while True:
            
                authinfo = await websocket.receive_json()
                #print(authinfo)
                authorization = authinfo["headers"]["Authorization"]
                current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
                if current_user:
                    try:
                        condition = f"email = '{current_user}'"
                        email_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.accountrevisioncards_table,condition=condition)
                        revisioncardfields = ("sendtoemail","subject","revisioncardtitle","revisionscheduleinterval","revisioncard","revisioncardimgname")
                        if email_exists:
                            for revisioncard in caesarcrud.get_large_data(revisioncardfields,caesarcreatetables.accountrevisioncards_table,condition=condition):
                                revisioncard = caesarcrud.tuple_to_json(revisioncardfields,revisioncard)
                                sendtoemail = revisioncard["sendtoemail"]
                                subject  = revisioncard["subject"]
                                revisioncardtitle = revisioncard["revisioncardtitle"]
                                revisioncardimgname = revisioncard.get("revisioncardimgname")
                                revisionscheduleinterval = revisioncard["revisionscheduleinterval"]
                                revisioncardtext = revisioncard["revisioncard"]
                                revisioncardhash = CaesarHash.hash_text(current_user + subject  + revisioncardtitle)
                                condition = f"revisioncardhash = '{revisioncardhash}'"
                                #print(condition)

                                if revisioncardimgname:
                                
                                    imagedata = caesarcrud.get_data(("revisioncardimgname","filetype","revisioncardhash","revisioncardimage"),caesarcreatetables.revisioncardimage_table,condition=condition)
                                    revisioncardimgname = [image["revisioncardimgname"] for image in imagedata]
                                    revisioncardimage = []
                                    
                                    for image in imagedata:

                                        imageb64_string =  caesarcrud.hex_to_base64(image["revisioncardimage"])

                                        final_imageb64 = f"{image['filetype']}{imageb64_string}"
                                        revisioncardimage.append(final_imageb64 )
                                    #print(revisioncardimage)
                                    await manager.broadcast(json.dumps({"revisioncardtitle":revisioncardtitle,"subject":subject,
                                        "revisionscheduleinterval":revisionscheduleinterval,"revisioncard":revisioncardtext,"revisioncardimgname":revisioncardimgname,"revisioncardimage":revisioncardimage,"sendtoemail":sendtoemail}))
                                
                                else:
                                    revisioncardimgname = []
                                    revisioncardimage = []
                                    await manager.broadcast(json.dumps({"revisioncardtitle":revisioncardtitle,"subject":subject,
                                                                          "revisionscheduleinterval":revisionscheduleinterval,"revisioncard":revisioncardtext,
                                                                          "revisioncardimgname":revisioncardimgname,"revisioncardimage":revisioncardimage,
                                                                          "sendtoemail":sendtoemail}))
                            
                            await manager.broadcast(json.dumps({"message":"all sent."}))
                            

                            #    await manager.broadcast(json.dumps(revisioncard)) # sends the buffer as bytes
                        elif not email_exists:
                            await manager.broadcast(json.dumps({"message":"No revision cards"}))
                            #return {"message":"No revision cards"} # Send in shape of data
                    except Exception as ex:
                        pass
                        #await manager.broadcast(json.dumps({f"error":f"{type(ex)},{str(ex)}"})) 
                elif not current_user:
                    await manager.broadcast(json.dumps({"message":"No user."}))
    except WebSocketDisconnect:
        #await websocket.close()
        manager.disconnect(websocket)
        ##await manager.broadcast(f"Client #{client_id} left the chat")
@app.post('/schedulerevisioncard') # POST # allow all origins all methods.
async def schedulerevisioncard(data : JSONStructure = None, authorization: str = Header(None)):     
    try:
        current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]



        if current_user:
            data = dict(data)#request.get_json() # test
            sendtoemail = data["sendtoemail"]
            revisioncard = data["revisioncards"][0]
            card = {"sendtoemail":sendtoemail,"subject":revisioncard["subject"],"revisioncardtitle":revisioncard["revisioncardtitle"],"revisioncard":revisioncard["revisioncard"]
                    ,"revisionscheduleinterval":revisioncard["revisionscheduleinterval"],
                    "revisioncardimgname":revisioncard["revisioncardimgname"],"revisioncardimgname":revisioncard["revisioncardimgname"],
                    "revisioncardimage":revisioncard["revisioncardimage"]}
            revisioncardhash = CaesarHash.hash_text(current_user + card["subject"]  + card["revisioncardtitle"])
            condition = f"revisioncardhash = '{revisioncardhash}'"
            schedule_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.schedule_table,condition=condition)
            if schedule_exists:
                return {"message":"revision cards scheduled"}
            else:
                #data["email"] = current_user 
                scheduleId = revisionbankcron.create_schedule(card,current_user)
                
                schedule_data = {"email":current_user,"revisioncardhash":revisioncardhash,"scheduleId":scheduleId}
                res = caesarcrud.post_data(("email","revisioncardhash","scheduleId"),(schedule_data["email"],schedule_data["revisioncardhash"],schedule_data["scheduleId"]),"scheduledcards")
                if res:
                    return {"message": "revision card scheduled"}
                return {"message": "revision card scheduled"}

    except Exception as ex:
        print(type(ex),ex)
        return {"error":f"{type(ex)},{ex}"}
@app.get('/getrevisioncards')# GET # allow all origins all methods.
async def getrevisioncards(authorization: str = Header(None)):
    def iter_df(user_revision_cards):
        for revisioncard in user_revision_cards["revisioncards"]:
            #print(revisioncard)
            revisioncard.update({"revisionscheduleinterval":revisioncard["revisionscheduleinterval"]})
            yield json.dumps(revisioncard)
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            condition = f"email = '{current_user}'"
            email_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.accountrevisioncards_table,condition=condition)
            if email_exists:  # Checks if email exists
                
                revisioncards = []
                for revisioncard in reversed(caesarcrud.get_data(("sendtoemail","subject","revisioncardtitle","revisionscheduleinterval","revisioncard","revisioncardimgname"),caesarcreatetables.accountrevisioncards_table,condition=condition)):
                    sendtoemail = revisioncard["sendtoemail"]
                    subject  = revisioncard["subject"]
                    revisioncardtitle = revisioncard["revisioncardtitle"]
                    revisioncardimgname = revisioncard.get("revisioncardimgname")
                    revisionscheduleinterval = revisioncard["revisionscheduleinterval"]
                    revisioncardtext = revisioncard["revisioncard"]
                    revisioncardhash = CaesarHash.hash_text(current_user + subject  + revisioncardtitle)
                    condition = f"revisioncardhash = '{revisioncardhash}'"
                    #print(condition)

                    if revisioncardimgname:
                        imagedata = caesarcrud.get_data(("revisioncardimgname","filetype","revisioncardhash","revisioncardimage"),caesarcreatetables.revisioncardimage_table,condition=condition)
                        revisioncardimgname = [image["revisioncardimgname"] for image in imagedata]
                        revisioncardimage = []
                        for image in imagedata:
                            imageb64_string = caesarcrud.hex_to_base64(image["revisioncardimage"])
                            final_imageb64 = f"{image['filetype']}{imageb64_string}"
                            revisioncardimage.append(final_imageb64 )
                    else:
                        revisioncardimgname = []
                        revisioncardimage = []
                    revisioncards.append({"revisioncardtitle":revisioncardtitle,"subject":subject,
                                                                          "revisionscheduleinterval":revisionscheduleinterval,"revisioncard":revisioncardtext,
                                                                          "revisioncardimgname":revisioncardimgname,"revisioncardimage":revisioncardimage,
                                                                          "sendtoemail":sendtoemail})
                        
                return {"revisionscheduleinterval":revisionscheduleinterval ,"revisioncards":revisioncards}
            elif not email_exists:
                return {"sendtoemail":sendtoemail,"message":"No revision cards"} # Send in shape of data
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/removerevisioncard') # POST # allow all origins all methods.
async def removerevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            subject = data["subject"]
            revisioncardtitle = data["revisioncardtitle"]
            revisioncardhash = CaesarHash.hash_text(current_user + subject  + revisioncardtitle)
            condition = f"revisioncardhash = '{revisioncardhash}'"
            res = caesarcrud.delete_data("accountrevisioncards",condition)
            res = caesarcrud.delete_data("revisioncardimages",condition)
            schedule_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.schedule_table,condition=condition)
            if schedule_exists:
                revsqlops.unschedule_card_qstash(condition)
                res = caesarcrud.delete_data("scheduledcards",condition=condition)
            return {"message":"revision card removed"}
        except Exception as ex:
            print({f"error":f"{type(ex)},{str(ex)}"})
            return {f"error":f"{type(ex)},{str(ex)}"}  
@app.get('/checkschedulerevisioncard')# GET # allow all origins all methods.
async def checkschedulerevisioncard(authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]

    if current_user:
        try:
            condition = f"email = '{current_user}'"
            schedule_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.schedule_table,condition=condition)
            if schedule_exists:  # Checks if email exists
                revisioncards =  caesarcrud.get_data(("revisioncardhash",),"accountrevisioncards",condition=f"email = '{current_user}'")
                scheduled_revisioncards = []
                for revisioncard in revisioncards:
                    #print(revisioncard)
                    rev_cards =  caesarcrud.get_data(("revisioncard",),"accountrevisioncards",condition=f"revisioncardhash = '{revisioncard['revisioncardhash']}'")
                    scheduled_cards =  caesarcrud.get_data(("scheduleId",),"scheduledcards",condition=f"revisioncardhash = '{revisioncard['revisioncardhash']}'")
                    if scheduled_cards:
                        rev_resp = {}
                        rev_resp.update(scheduled_cards[0])
                        rev_resp.update(rev_cards[0])
                        scheduled_revisioncards.append(rev_resp)
                    else:
                        pass

                return {"revisioncards":scheduled_revisioncards}
            elif not schedule_exists:
                return {"message":"revision cards not scheduled"} # Send in shape of data
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/unschedulerevisioncard') # POST # allow all origins all methods.
async def unschedulerevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            subject = data["subject"]
            revisioncardtitle = data["revisioncardtitle"]
            revisioncardhash = CaesarHash.hash_text(current_user + subject  + revisioncardtitle)
            condition = f"revisioncardhash = '{revisioncardhash}'"
            revsqlops.unschedule_card_qstash(condition)
            res = caesarcrud.delete_data("scheduledcards",condition=condition)
            if res:
                return {"message":"revision card unscheduled"}
            else:
                return {"error":"error when unscheduling."}

            #    
          
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.delete('/unscheduleallrevisioncard') # DELETE # allow all origins all methods.
async def unscheduleallrevisioncard(authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            schedule_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.schedule_table,condition=f"email = '{current_user}'")
            if schedule_exists:
                scheduled_cards =  caesarcrud.get_data(("revisioncardhash","scheduleId"),"scheduledcards",condition=f"email = '{current_user}'")
                for card in scheduled_cards:
                    revisioncardhash = card["revisioncardhash"]
                    condition = f"revisioncardhash = '{revisioncardhash}'"
                    revsqlops.unschedule_card_qstash(condition)
                    res = caesarcrud.delete_data("scheduledcards",condition=condition)


                        
                return {"message":"Allrevision card unscheduled"}
        except Exception as ex:
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/sendnowrevisioncard') # POST # allow all origins all methods.
async def sendnowrevisioncard(data : JSONStructure = None, authorization: str = Header(None)):
    try:

        current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
        if current_user:
            data = dict(data)
            #print(data)
            revisioncard = data["revisioncards"][0]
            revisioncardtext = revisioncard["revisioncard"].replace("\n","<br>",10000)
            revisioncardtitle = data['revisioncards'][0]['revisioncardtitle']
            message = f"""{revisioncardtitle}<br>{revisioncardtext}"""

            if revisioncard.get("revisioncardimgname"):
                revisioncardimgname = revisioncard.get("revisioncardimgname")
                revisioncardimage = revisioncard.get("revisioncardimage")
                CaesarAIEmail.send(**{"email":data["sendtoemail"],"message":message,"subject":f"{data['revisioncards'][0]['subject']} | {revisioncardtitle} - {current_user}","attachment":dict(zip(revisioncardimgname,revisioncardimage))})
                

            else:
                CaesarAIEmail.send(**{"email":data["sendtoemail"],"message":message,"subject":f"{data['revisioncards'][0]['subject']} | {revisioncardtitle} - {current_user}"})

            return {"message":"revision card sent"}
    except Exception as ex:
        print({f"error":f"{type(ex)},{str(ex)}"})
        return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/sendscheduledrevisioncard') # POST # allow all origins all methods.
async def sendnowrevisioncard(data : JSONStructure = None):
    try:


        data = dict(data)
        #print(data)
        # {'sendtoemail': 'amari.lawal@gmail.com', 'subject': 'Technology for an Organizational Context', 'revisioncardtitle': '3.1 Topic 3: The Impact of IS on the organisation and business strategy', 'revisioncard': 'Technology for an Organizational Context<br>3.1 Topic 3: The Impact of IS on the organisation and business strategy<br>Resource: https://canvas.qa.com/courses/2751/pages/3-dot-1-topic-3-the-impact-of-is-on-the-organisation-and-business-strategy?module_item_id=323429<br>hello', 'revisionscheduleinterval': '16H', 'revisioncardimgname': [], 'revisioncardimage': []}
        sendtoemail = data["sendtoemail"]
        current_user = data["email"]
        subject = data["subject"]
        revisioncardtext = data["revisioncard"].replace("\n","<br>",1000000)
        revisioncardtitle = data['revisioncardtitle']
        message = f"""{revisioncardtitle}<br>{revisioncardtext}"""

        if data.get("revisioncardimgname"):
            revisioncardimgname = data.get("revisioncardimgname")
            revisioncardimage = data.get("revisioncardimage")
            CaesarAIEmail.send(**{"email":sendtoemail,"message":message,"subject":f"{subject} | {revisioncardtitle} - {current_user}","attachment":dict(zip(revisioncardimgname,revisioncardimage))})
            

        else:
            CaesarAIEmail.send(**{"email":sendtoemail,"message":message,"subject":f"{subject} | {revisioncardtitle} - {current_user}"})

        return {"message":"revision card sent"}
    except Exception as ex:
        print({f"error":f"{type(ex)},{str(ex)}"})
        return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/managechangecardimage') # POST # allow all origins all methods.
async def managechangecardimage(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            oldcard_data = {"subject":data["subject"],"revisioncardtitle":data["revisioncardtitle"],"oldimagename":data["oldimagename"],"newimagename":data["newimagename"],"newimage":data["newimage"]}
            oldrevisioncardimgname = oldcard_data["oldimagename"]
            newrevisioncardimgname = oldcard_data["newimagename"]
            newimage = oldcard_data["newimage"]
            
            # TODO Slightly buggy here - removes old schedule from the database.
            subject = oldcard_data["subject"]
            revisioncardtitle = oldcard_data["revisioncardtitle"]
            revisioncardhash = CaesarHash.hash_text(current_user + subject  + revisioncardtitle)
            condition = f"revisioncardhash = '{revisioncardhash}'"
            schedule_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.schedule_table,condition=condition)
            if schedule_exists:
                revsqlops.unschedule_card_qstash(condition)
                res = caesarcrud.delete_data("scheduledcards",condition=condition)
            res = revsqlops.update_revisoncard_image(current_user,newrevisioncardimgname,newimage,revisioncardhash,oldrevisioncardimgname)
            if res:
                return {"message":"revisioncard image was replaced."}
            else:
                return {"error":"error when updating."}
                #return {"message":"revision card meta data changed."}
        except Exception as ex:
            #print({f"error":f"{type(ex)},{str(ex)}"})
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/manageaddcardimage') # POST # allow all origins all methods.
async def manageaddcardimage(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            oldcard_data = {"subject":data["subject"],"revisioncardtitle":data["revisioncardtitle"],"newimagename":data["newimagename"],"newimage":data["newimage"]}
            subject = oldcard_data["subject"]
            revisioncardtitle = oldcard_data["revisioncardtitle"]
            # TODO Slightly buggy here - removes old schedule from the database.
            revisioncardhash = CaesarHash.hash_text(current_user + subject  + revisioncardtitle)
            condition = f"revisioncardhash = '{revisioncardhash}'"
            schedule_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.schedule_table,condition=condition)
            if schedule_exists:
                revsqlops.unschedule_card_qstash(condition)
            condition_image = f"revisioncardhash = '{revisioncardhash}' AND revisioncardimgname = '{data['newimagename']}' AND email = '{current_user}'"
            image_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.revisioncardimage_table,condition=condition_image)
            if not image_exists:
                res = revsqlops.store_revisoncard_image(current_user,oldcard_data["newimagename"],oldcard_data["newimage"],revisioncardhash)
                if res:
                    return {"message":"revisioncard image was added."}

                else:
                    return {"error":"error when adding image."}
            else:
                return {"message":"image already exists."}
        except Exception as ex:
            #print({f"error":f"{type(ex)},{str(ex)}"})
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.post('/manageremovecardimage') # POST # allow all origins all methods.
async def manageremovecardimage(data : JSONStructure = None, authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if current_user:
        try:
            data = dict(data)#request.get_json()
            oldcard_data = {"subject":data["subject"],"revisioncardtitle":data["revisioncardtitle"],"oldimagename":data["oldimagename"]}
            oldimagename = oldcard_data["oldimagename"]
            subject = oldcard_data["subject"]
            revisioncardtitle = oldcard_data["revisioncardtitle"]
            # TODO Slightly buggy here - removes old schedule from the database.
            revisioncardhash = CaesarHash.hash_text(current_user + subject  + revisioncardtitle)
            condition = f"revisioncardhash = '{revisioncardhash}'"
            schedule_exists = caesarcrud.check_exists(("*"),table=caesarcreatetables.schedule_table,condition=condition)
            #if schedule_exists:
            #    revsqlops.unschedule_card_qstash(condition)
            res =caesarcrud.delete_data("revisioncardimages",f"revisioncardhash = '{revisioncardhash}' AND revisioncardimgname = '{oldimagename}' AND email = '{current_user}'")
            images_exist = caesarcrud.check_exists(("*"),"revisioncardimages",f"revisioncardhash = '{revisioncardhash}' AND email = '{current_user}'")
            print(images_exist)
            if not images_exist:
                print("hi")
                res = caesarcrud.update_data(("revisioncardimgname",),("NULL",),"accountrevisioncards",condition=f"revisioncardhash = '{revisioncardhash}' AND email = '{current_user}'")

            if res:
                return {"message":"revisioncard image was deleted."}
                #return {"message":"revision card meta data changed."}
            else:
                return {"error":"error when deleting data."}
        except Exception as ex:
            #print({f"error":f"{type(ex)},{str(ex)}"})
            return {f"error":f"{type(ex)},{str(ex)}"}
@app.get('/getsubscription') # GET
async def getsubscription(authorization: str = Header(None)):
    try:
        current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
        if current_user:
            
                subscription_exists = caesarcrud.check_exists(("*"),table="users",condition=f"email = '{current_user}'")
                #if subscription_exists:
                #end_date = user_from_db["end_date_subscription"]
                #end_date_subscription = {"end_date_subscription": end_date}
                return {"error":"no subscription system yet."}
    except Exception as ex:
        return {"error": f"{type(ex)}-{ex}"}
@app.delete('/deleteaccount') # DELETE
async def deleteaccount(authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            res = caesarcrud.delete_data("users",condition=f"email = '{current_user}'")
            res = caesarcrud.delete_data("accountrevisioncards",condition=f"email = '{current_user}'")
            res = caesarcrud.delete_data("revisioncardimages",condition=f"email = '{current_user}'")
            res = caesarcrud.delete_data("scheduledcards",condition=f"email = '{current_user}'")
            if res:
                return {"message":"Account Deleted"}
            else:
                return {"error":"error when deleting."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/checkstudentsubscriptions') # GET
async def checkstudentsubscriptions(authorization: str = Header(None)): 
    try:
        current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
        if current_user:
            
                #student_from_db = list(importcsv.db.studentsubscriptions.find({"email": current_user}))[0] # Gets wanted data for user
                #student_subscription  = student_from_db["subscription"]
                #student_subscription_json = {"student_subscription": student_subscription}
                return {"error":"studentsubscription doesn't exist yet."}#student_subscription_json
    except Exception as ex:
        return {"error": f"{type(ex)}-{ex}"}
@app.get('/getemailcount') # GET
async def getemailcount(authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try:
            #user_from_db = list(importcsv.db.users.find({"email": current_user}))[0] # Gets wanted data for user
            #emailcount = user_from_db["emailsleft"]
            #emailcountres = {"emailcount": emailcount}
            return {"error":"no subscription system yet."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/getfreetrial') # GET
async def getfreetrial(authorization: str = Header(None)):
    current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
    if current_user:
        try: 
            #freetrialhistory = list(importcsv.db.freetrialhistory.find({"email": current_user}))[0] # Gets wanted data for user
            #freetrial = freetrialhistory["freetrial"]
            #freetrial_subscription = {"freetrial": freetrial} # check freetrial
            return {"error":"no subscription system yet."}
        except Exception as ex:
            return {"error": f"{type(ex)}-{ex}"}
@app.get('/getemail') # GET
async def getemail(authorization: str = Header(None)):
    try: 
        current_user = revisionbankjwt.secure_decode(authorization.replace("Bearer ",""))["email"] # outputs the email of the user example@gmail.com
        print(current_user)
        if current_user:
            
                email = caesarcrud.get_data(("email",),"users",condition=f"email = '{current_user}'")[0]
                return {"email":email["email"]}
    except Exception as ex:
        return {"error": f"{type(ex)}-{ex}"}

async def main():
    config = uvicorn.Config("main:app", port=8080, log_level="info",reload=True) # ,host="0.0.0.0"
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    #print(image_data)

    #images_data = caesarcrud.get_large_data(("revisioncardimgname","email","filetype","revisioncardhash","revisioncardimage"),"revisioncardimages")
    #for image in images_data:
    #    revisioncard = caesarcrud.tuple_to_json(("revisioncardimgname","email","filetype","revisioncardhash"),image)
    #    res = caesarcrud.update_data(("revisioncardimgname",),("true",),"accountrevisioncards",f"revisioncardhash = '{revisioncard['revisioncardhash']}'")
    #    print(revisioncard['revisioncardhash'])
    uvicorn.run("main:app",port=8080,log_level="info")
    #uvicorn.run()
    #asyncio.run(main())