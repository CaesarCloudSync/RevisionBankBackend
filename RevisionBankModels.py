from typing import Generic, TypeVar,Dict,List,AnyStr,Any,Union
from pydantic import BaseModel
from pydantic.generics import GenericModel

M = TypeVar("M", bound=BaseModel)


class GenericSingleObject(GenericModel, Generic[M]):
    object: M
class RevisionBankAuth(BaseModel):
    email:str
    password:str

