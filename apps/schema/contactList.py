
from pydantic import BaseModel
from typing import List
from sqlmodel import SQLModel
from ..models.models import Contact, ListContact


class contactlist(SQLModel):
    id: int
    list_name: str
   

class contactlistCreate(SQLModel):
    list_name: str


class contactlistRead(contactlist):
    pass    

class contactlistUpdate(SQLModel):
    list_name: str



