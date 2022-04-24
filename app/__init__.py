from flask import Flask
app = Flask(__name__) #to avoid circular import
from app import views 
from app import api_views 
