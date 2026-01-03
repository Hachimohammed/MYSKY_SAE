from flask import Flask

app = Flask(__name__, static_url_path='/static')






app.secret_key='ma cle secrete unique' 

app.config["SESSION_COOKIE_SECURE"] = True 
from app.controllers import *
