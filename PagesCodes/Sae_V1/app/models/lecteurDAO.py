import sqlite3
from app import app
from app.models.lecteur import User
from app.models.lecteurDAOInterface import lecteurDAOInterface

def lecteurDAO(lecteurDAOInterface):

    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
        self.server_adresse = None
        self.gateway = None
        self.subnet_mask = None
        self.dns_server = None
    
    def setServer(self,server_adresse,gateway,subnet_mask,dns_server):
        self.server_adresse = server_adresse
        self.gateway = gateway
        self.subnet_mask = subnet_mask
        self.dns_server = dns_server

    def findPlayer(self):
        detected = []