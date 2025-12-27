import sqlite3
from ping3 import *
import subprocess
from app import app
from app.models.lecteur import BDDAao
from app.models.lecteurDAOInterface import lecteurDAOInterface

def lecteurDAO(lecteurDAOInterface):

    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
        self.database.init
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


    def findStatut(self):
        """
        
        Le programme marche trés bien (tester avec une version test sur une machine) MAIS
        les sockets RAW nécessite des privilgés DONC EXECUTER SUDO

        """
        
        conn = self.DatabaseInit._getDBConnection()
        try:
            ip_adresse = conn.execute('SELECT DISTINCT adresse_ip FROM lecteur').fetchall()
            for ip in ip_adresse:
                delay = ping(ip,timeout=4)

                if delay is not None and delay is not False:
                    conn.execute("UPDATE lecteur SET statut = 'UP' WHERE adresse_ip = (?)",ip)
                else:
                    pass # DOWNN étant définie par défaut
            print("Programme executer à la perfection")
        except Exception as e:
            print(f"Erreur {e} dans le programme")




