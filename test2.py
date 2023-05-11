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
from config import Config
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
time_hour = 60 * 60 # 1 hour,

with open("tets.json","r") as f:
    user_revision_cards = json.load(f)

@app.get('/')# GET # allow all origins all methods.
async def index():
    return "Hello World"

@app.get('/getrevisioncards')# GET # allow all origins all methods.
async def getrevisioncards():
    def iter_df(user_revision_cards):
        for revisioncard in user_revision_cards:
            print(revisioncard)
            yield json.dumps(revisioncard)
    with open("tets.json","r") as f:
        user_revision_cards= json.load(f)["revisioncards"]

    try:

        return StreamingResponse(iter_df(user_revision_cards), media_type="application/json")
        #return user_revision_cards

    except Exception as ex:
        return {f"error":f"{type(ex)},{str(ex)}"}
    #200OK, 62 ms, 19.89 KB
@app.websocket("/caesarobjectdetectws")
async def caesarobjectdetectws(websocket: WebSocket):
    # listen for connections
    await websocket.accept()

    try:
        while True:
            contents = await websocket.receive_json()
            print(contents)
            if contents["message"] == "getcards":
                for revisioncard in user_revision_cards["revisioncards"]:
                    await websocket.send_json(json.dumps(revisioncard)) # sends the buffer as bytes


    except WebSocketDisconnect:
        print("Client disconnected")


async def main():
    config = uvicorn.Config("test2:app", port=7860, log_level="info",host="0.0.0.0",reload=True)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())