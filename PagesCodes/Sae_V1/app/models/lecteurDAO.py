import sqlite3
from ping3 import *
import subprocess
import json
import requests
from app import app
from app.models.lecteur import BDDAao
from app.models.lecteurDAOInterface import lecteurDAOInterface

def lecteurDAO(lecteurDAOInterface):

    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
        self.database.init()
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

        """
        Méthode findPlayer du DAO qui consiste à partir de la commande status de tailnet et de son 
        option --json trouve automatiquement les machines dont leurs noms (nom que vous avez données à la machine)
        et leurs adresse iP soient récuperer et intégrer à une liste de machines , ensuite il manque la localisation 
        on va utiliser le site 'ipinfo.ip' pour tout sa on va récuperer la ville données par le site
        ensuite on intégre tout sa à la bdd
        
        """

        try:
            conn = self.DatabaseInit._getDBConnection()

            players = {}
            
            cmd = subprocess.run(
                ["tailscale","status","--json"],
                capture_output=True,
                text = True
            )

            data = json.loads(cmd.stdout)

            for peer in data['Peer'].values:
                name = peer['Hostname']
                ip = peer['TailscalesIPs'][0]

                if name not in players:
                    players[name] = {
                        "name" : name,
                        "ip" : ip,
                        "Localisation" : None
                    }

            for player in players:
                if players[player]['Localisation'] == None:
                    ip = players[player]['ip']
                    res = requests.get(f"https://ipinfo.io/{ip}/json")
                    loc_data = res.json()
                    players[player]['Localisation'] = res['City']


            for player in players:
                conn.execute("INSERT OR IGNORE INTO lecteur (nom_lecteur,adresse_ip,emplacement)" 
                "VALUES (?,?,?)",players[player]['name'],players[player]['ip'],players[player]['Localisation'])
                    

        except Exception as e:
            print(f"erreur {e} dans findPlayer")


    def AppendPlayerManually(self,adresse_ip,nom_lecteur,emplacement):

        """
        Fonction qui consiste en cas de par exemple non réponse de tailnet (ce qui peut peut-être arriver)
        de rajouter des machines 
        C'est le seul cas ou on utilisera cette fonction
        
        """

        conn = self.DatabaseInit._getDBConnection()

        conn.execute("INSERT OR IGNORE INTO lecteur (nom_lecteur,adresse_ip,emplacement)" 
        "VALUES (?,?,?)",nom_lecteur,adresse_ip,emplacement)




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
            print(f"Erreur {e} dans findStatut")




