import sqlite3
from ping3 import *
import subprocess
import json
import requests
from pathlib import Path
from mpd import MPDClient
import datetime
from app import app
from app.models.BDDao import BDDAao
from app.models.logDAO import logDAO
from app.models.lecteurDAOInterface import lecteurDAOInterface

def lecteurDAO(lecteurDAOInterface):

    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
        self.log = logDAO()

    
    def _getDBConnection(self):
        """Obtient une connexion à la base de données"""
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def findPlayer(self):

        """
        Méthode findPlayer du DAO qui consiste à partir de la commande status de tailnet et de son 
        option --json trouve automatiquement les machines dont leurs noms (nom que vous avez données à la machine)
        et leurs adresse iP soient récuperer et intégrer à une liste de machines , ensuite il manque la localisation 
        on va utiliser le site 'ipinfo.ip' pour tout sa on va récuperer la ville données par le site
        ensuite on intégre tout sa à la bdd
        
        """

        try:
            conn = self._getDBConnection()

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
                "VALUES (?,?,?)",player['name'],player['ip'],player['Localisation'])
                self.log.addEvent("joueur trouver",f"insertion de {player["name"]}",datetime.now(),)
                conn.commit()
                conn.close()
                    

        except Exception as e:
            print(f"erreur {e} dans findPlayer")


    def AppendPlayerManually(self,adresse_ip,nom_lecteur,emplacement):

        """
        Fonction qui consiste en cas de par exemple non réponse de tailnet (ce qui peut peut-être arriver)
        de rajouter des machines 
        C'est le seul cas ou on utilisera cette fonction
        
        """

        conn = self._getDBConnection()

        conn.execute("INSERT OR IGNORE INTO lecteur (nom_lecteur,adresse_ip,emplacement)" 
        "VALUES (?,?,?)",nom_lecteur,adresse_ip,emplacement)
        conn.commit()
        conn.close()




    def findStatut(self):
        """
        
        Le programme marche trés bien (tester avec une version test sur une machine) MAIS
        les sockets RAW nécessite des privilgés DONC EXECUTER SUDO

        """
        
        conn = self._getDBConnection()
        try:
            ip_adresse = conn.execute('SELECT DISTINCT adresse_ip FROM lecteur').fetchall()
            for ip in ip_adresse:
                delay = ping(ip,timeout=4)

                if delay is not None and delay is not False:
                    conn.execute("UPDATE lecteur SET statut = 'UP' WHERE adresse_ip = (?)",ip)
                else:
                    conn.execute("UPDATE lecteur SET statut = 'DOWN' WHERE adresse_ip = (?)",ip)
            print("Programme executer à la perfection")
        except Exception as e:
            print(f"Erreur {e} dans findStatut")

    def Sync(self,adresse_ip):

        """
        Synchronise un lecteur données

        """


        try:

            conn = self._getDBConnection()

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

    def SyncAll(self):

        """
        Synchronise tout les lecteurs
        """

        try:

            conn = self._getDBConnection()

            cmd = ['sudo','tailscale', 'up', '--reset']

            success, output = self._execute_command(cmd)

            ips = conn.execute("SELECT ip_adresse FROM lecteur").fetchAll()

            for ip in ips:

                delay = ping(ip,timeout=4)

                if success:
                    if delay is not None and delay is not False:
                        conn.execute("UPDATE lecteur SET statut = 'UP' WHERE adresse_ip = (?)",(ip,))
                    else:
                        print('erreur ping')
                else:
                    print('echec avec la commande up')
        
        except Exception as e:
            print(f'Erreur {e} dans Sync')

    


    def pullMP3toPlayers(self):
        try:
            """
            Méthode qui consiste à pull les differents fichiers dans le dossier audio à l'aide de 
            l'API conçu par Mohamed Hachim
            """

            conn = self._getDBConnection()

            get = requests.get(f"http://127.0.0.1:5000/api/v1/audio/list")
            json = get.json

            hosts= conn.execute("SELECT nom_lecteur,adresse_ip FROM lecteur").fetchall()

            for file in json['data']['chemin_fichier'].values:
                for nom_lecteur,adresse_ip in hosts:
                    cmd = [
                    "rsync", "-avz", "--progress",
                    f"{file}/",
                    f"{nom_lecteur}@{adresse_ip}:~/musique/"]

                    res = subprocess.run(cmd, capture_output=True, text=True)

                if res.returncode == 0: 
                    # tout va bien
                    
                    update_mpd = ["ssh", f"{nom_lecteur}@{adresse_ip}", "mpc -p 6601 update"]
                    subprocess.run(update_mpd, capture_output=True)

                else:
                        findStatut()


        except Exception as e:
            print(f"Erreur {e} dans pullMP3toPlayers")


    def Pullm3uToPlayers(self):
        """
        Même logique 
        """
        try:
            conn = self._getDBConnection()

            get = requests.get(f"http://127.0.0.1:5000/api/v1/audio/list")
            json = get.json()

            conn = self.DatabaseInit._getDBConnection()
            hosts = conn.execute('SELECT DISTINCT nom,adresse_ip FROM lecteur').fetchall()



            for file in json['playlists']['nom_playlist'].values:
            
                f = f"~/MYSKY_SAE/PagesCodes/SAE_V2/app/static/playlists/{file}"

 

                for nom,adresse_ip in hosts:
                    cmd = [
                    "rsync", "-avz", "--progress",
                    f"{f}/",
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

        """
        
        Recupere les informations d'une playlist et joue la playlist associer aux jours de lecture
        grâce à l'API de la Playlist

        """

        try:
        
            client = MPDClient()

            jours = ["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI","SAMEDI","DIMANCHE"]

            get = requests.get(f"http://127.0.0.1:5000/api/v1/playlists")
            json = get.json

            now = datetime.datetime.now()
            jour_actuel = jours[now.weekday()] 
            str_date = datetime.now().strftime("%Y%m%d")



            conn = self._getDBConnection()
            ips = conn.execute("SELECT adresse_ip FROM lecteur").fetchall()

            for file in json['playlists'].values:
                
                    f = f"~/MYSKY_SAE/PagesCodes/SAE_V2/app/static/playlists/{file["nom_playlist"]}"
                    
                    for ip in ips:
                        client.connect(ip,6601)
                        if file["jour_semaine"] == jour_actuel :
                            MPDClient.load(f)
                            MPDClient.play(1)
                        client.close()
                        client.disconnect()

        except Exception as e:
            print(f"Erreur {e} dans la méthode playm3ubydayandtimestamp")

    def Ad(self,mp3):

            """
            Methode pour mettre en pause un playlist jouer un mp3 pour 
            le commercial relancer la playlist là ou elle en était 

            """

            try:

                client = MPDClient()

                conn = self._getDBConnection()
                ips = conn.execute("SELECT adresse_ip FROM lecteur").fetchall()

                for ip in ips:
                        client.connect(ip,6601)
                        status = client.status()
                        playlist_pos = status['song']
                        playlist_index = status['playlist']
                        playlist_state = status['state']

                        if playlist_state == "play":
                            client.pause(1)
                        
                        client.add = mp3
                        client.add(mp3)
                        client.play()

                        duree = int(client.currentsong()["time"][0]) 
                        time.sleep(duree + 1)

                        client.delete(-1) # supprime le dernier son ajoute

                        client.play(playlist_pos)

                        client.close()
                        client.disconnect()
            except Exception as e:
                print(f"Erreur {e} dans la méthode Ad")


    def WhatPlayerPlaying(self):

        """
        Retourne assez d'element qui nous indique ce que les lecteurs jouent et 
        ou elles en sont 
        """

        try:

                client = MPDClient()

                conn = self._getDBConnection()
                ip = conn.execute("SELECT adresse_ip FROM lecteur").fetchone()
                if ip:
                        client.connect(ip,6601)
                        status = client.status()
                        song = client.currentSong()
                        elapsed = status["elapsed"][0]
                        duration = song["time"][0]
                        file = song["file"]
                        name = song["title"]

                        return {
                            "file":file,
                            "name":name,
                            "elapsed":elapsed,
                            "duration":duration
                        }
                
        except Exception as e:
            print(f"Erreur {e} dans la méthode WhatPlayersPlaying")


    def getAllPlayer(self):

        try:
            players = {}
            conn= self._getDBConnection()
            hosts = conn.execute("SELECT * FROM lecteur").fetchAll()

            for host in hosts:
                if host not in players:
                    players.append(dict[host])

            return players
            
        except Exception as e:
            print(f"Erreur {e} dans getAllPlayer")

    
    def findByIP(self,adresse_ip):

        try:
            players = {}
            conn= self._getDBConnection()
            hosts = conn.execute("SELECT * FROM lecteur WHERE adresse_ip = (?)",(adresse_ip,)).fetchAll()

            for host in hosts:
                if host not in players:
                    players.append(dict[host])

            return players
            
        except Exception as e:
            print(f"Erreur {e} dans findByIP")

        

                


    
    def getAllUp(self):
            
            """
            Retourne tout les lecteurs en état de marche et de synchronisité

            """
            
            try:

                up = []
                conn = self._getDBConnection()
                hosts = conn.execute('SELECT DISTINCT * FROM lecteur WHERE statut = UP').fetchall()

                for host in host:
                    if host not in up:
                        up.append(host)

                return up

            except Exception as e:
                print(f"Erreur {e} dans getAllUp")


    def getAllDown(self):

        """
            Retourne tout les lecteurs qui ne sont âs en état de marche et de synchronisité
            
        """
            
        try:

            down = []
            conn = self._getDBConnection()
            hosts = conn.execute('SELECT DISTINCT * FROM lecteur WHERE statut = DOWN').fetchall()

            for host in host:
                if host not in down:
                    down.append(host)

            return down

        except Exception as e:
            print(f"Erreir {e} dans getAllDown")

                 

    



    



