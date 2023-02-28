from pydantic import BaseModel, Field
from typing import Optional 
from bson.objectid import ObjectId
import bcrypt
import hashlib
# https://www.mongodb.com/developer/how-to/flask-python-mongodb/
# https://codehandbook.org/creating-rest-api-using-python-mongodb/
# https://zetcode.com/python/bcrypt/
class PydanticObjectID(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise TypeError(f'Must be an ObjectId')
        return str(v)
class Users(BaseModel):
    id : PydanticObjectID # Sets MongoDB ID 
    email: str
    password: str
    access: bool
    def generate_hash_pw(self):
        salt = bcrypt.gensalt()
        data = self.dict(by_alias=True, exclude_none=True)
        hashed = bcrypt.hashpw(data["password"].encode('utf-8'), salt)
        return hashed,str(salt).replace("b'","").replace("'","")
    
    def to_bson(self):
        data = self.dict(by_alias=True,exclude_none=True)
        hashed = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
        del data["password"]
        data["password"] = hashed
        data["_id"] = data["id"]
        del data["id"]
        return data
        #data_val = json.loads(json_util.dumps(data))

