#from flask_mongoengine import Document
from mongoengine import StringField
from flask_pymongo import Document

class Doctor(Document):
    doctor_id = StringField(primary_key=True)
    name = StringField(required=True)
    specialty = StringField(required=True)
