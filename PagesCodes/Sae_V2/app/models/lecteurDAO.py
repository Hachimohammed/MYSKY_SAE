import sqlite3
from ping3 import *
import subprocess
import json
import requests
from pathlib import Path
import datetime
from app import app
from app.models.lecteur import BDDAao
from app.models.lecteurDAOInterface import lecteurDAOInterface

def lecteurDAO(lecteurDAOInterface):

    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
        self.database.init()

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
                    players[player]['Localisation'] = loc_data['City']


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
                    return True
                else:
                    return False
            print("Programme executer à la perfection")
        except Exception as e:
            print(f"Erreur {e} dans findStatut")

def Sync(self,adresse_ip):

    try:

        conn = self.DatabaseInit._getDBConnection()

        cmd = ['sudo','tailscale', 'up', '--reset']

        success, output = self._execute_command(cmd)

        delay = ping(adresse_ip,timeout=4)

        if success:
            if delay is not None and delay is not False:
                conn.execute("UPDATE lecteur SET statut = 'UP' WHERE adresse_ip = (?)",(adresse_ip,))
            else:
                print('erreur ping')
        else:
            print('echec avec la commande up')
    
    except Exception as e:
        print(f'Erreur {e} dans Sync')

    


def pullMP3toPlayers(self):
    try:
        """
        Méthode qui consiste à pull les differents fichiers dans le dossier audio (qui 
        sont directement importer grace à AudioFileService et autres services) 
        """
        source_dir = '~/MYSKY_SAE/PagesCodes/SAE_V2/app/static/audio'

        conn = self.DatabaseInit._getDBConnection()
        hosts = conn.execute('SELECT DISTINCT nom,adresse_ip FROM lecteur').fetchall()

        for nom,adresse_ip in hosts:
            cmd = [
            "rsync", "-avz", "--progress",
            "--include", "*/",
            "--include", "*.mp3",
            "--exclude", "*",
            f"{source_dir}/",
            f"{nom}@{adresse_ip}:~/musique/"]

            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode == 0: 
                # tout va bien
                
                update_mpd = ["ssh", f"{nom}@{adresse_ip}", "mpc -p 6601 update"]
                subprocess.run(update_mpd, capture_output=True)

            else:
                self.findStatut()
                if findStatut() == False:
                    print("Pas Synchro")


    except Exception as e:
        print(f"Erreur {e} dans pullMP3toPlayers")

def Pullm3uToPlayers(self):
    """
    Même logique 
    """
    try:
        source_dir = '~/MYSKY_SAE/PagesCodes/SAE_V2/app/static/playlists'

        conn = self.DatabaseInit._getDBConnection()
        hosts = conn.execute('SELECT DISTINCT nom,adresse_ip FROM lecteur').fetchall()

        for nom,adresse_ip in hosts:
            cmd = [
            "rsync", "-avz", "--progress",
            "--include", "*/",
            "--include", "*.m3u",
            "--exclude", "*",
            f"{source_dir}/",
            f"{nom}@{adresse_ip}:~/musique/"]

            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode == 0: 
                # tout va bien
                
                update_mpd = ["ssh", f"{nom}@{adresse_ip}", "mpc -p 6601 update"]
                subprocess.run(update_mpd, capture_output=True)
            
            else:

                self.findStatut()

    except Exception as e:
        print(f"erreur {e} dans Pullm3uToPlayers")

def playm3ubydayandtimestamp(self):

    jours = ["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI","SAMEDI","DIMANCHE"]

    now = datetime.datetime.now()
    jour_actuel = jours[now.weekday()]  
    date_actuelle = now.strftime("%Y%m%d")  


def getAllUp(self):

        up = []
        conn = self.DatabaseInit._getDBConnection()
        hosts = conn.execute('SELECT DISTINCT * FROM lecteur WHERE statut = UP').fetchall()

        for host in host:
            if host not in up:
                up.append(host)

def getAllDown(self):

        down = []
        conn = self.DatabaseInit._getDBConnection()
        hosts = conn.execute('SELECT DISTINCT * FROM lecteur WHERE statut = DOWN').fetchall()

        for host in host:
            if host not in down:
                down.append(host)

                 

    



    



