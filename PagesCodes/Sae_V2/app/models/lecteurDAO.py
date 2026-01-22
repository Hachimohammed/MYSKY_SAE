import sqlite3
from ping3 import *
import subprocess
import json
import requests
import time
from pathlib import Path
from mpd import MPDClient
from datetime import datetime
from app import app
from app.models.lecteur import lecteur
from app.models.BDDao import DatabaseInit
from app.models.lecteurDAOInterface import lecteurDAOInterface

class lecteurDAO(lecteurDAOInterface):

    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
    
    def _getDBConnection(self):
        """Obtient une connexion à la base de données"""
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def findPlayer(self):
        """
        Trouve automatiquement les machines via Tailscale et les ajoute à la BDD
        """
        try:
            conn = self._getDBConnection()
            players = {}
            
            cmd = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True,
                text=True
            )

            data = json.loads(cmd.stdout)

            for peer in data['Peer'].values():
                name_before_split = peer['HostName']
                name = name_before_split.split('-')[0]
                ip = peer['TailscaleIPs'][0]

                if name not in players:
                    players[name] = {
                        "name": name,
                        "ip": ip,
                        "ville": None,
                        "latitude": None,
                        "longitude": None
                    }

            for player in players:
                if players[player]['ville'] is None:
                    curl = 'curl -s https://api.ipify.org'
                    ssh_curl = f'ssh {players[player]["name"]}@{players[player]["ip"]} "{curl}"'
                    curl_res = subprocess.run(ssh_curl, shell=True, capture_output=True, text=True, timeout=35)
                    public_ip = curl_res.stdout.strip()

                    res = requests.get(f"https://ipinfo.io/{public_ip}/json")
                    loc_data = res.json()
                    players[player]['ville'] = loc_data['city']
                    lat_long = loc_data["loc"]
                    latitude, longitude = map(float, lat_long.split(','))
                    players[player]['latitude'] = latitude
                    players[player]['longitude'] = longitude

                    conn.execute("INSERT OR IGNORE INTO localisation (ville, latitude, longitude) VALUES (?, ?, ?)",
                                (players[player]['ville'], players[player]['latitude'], players[player]['longitude']))
                    conn.commit()

                    id_localisation = conn.execute("SELECT id_localisation FROM localisation WHERE ville = ?",
                                                    (players[player]['ville'],)).fetchone()

                    conn.execute("INSERT OR IGNORE INTO lecteur (nom_lecteur, adresse_ip, statut, id_localisation) VALUES (?, ?, ?, ?)",
                                (players[player]['name'], players[player]['ip'], "UP", id_localisation[0]))
                    conn.commit()

            conn.close()

        except Exception as e:
            print(f"Erreur {e} dans findPlayer")

    def AppendPlayerManually(self, adresse_ip, nom_lecteur):
        """Ajoute manuellement un lecteur"""
        conn = self._getDBConnection()
        conn.execute("INSERT OR IGNORE INTO lecteur (nom_lecteur, adresse_ip, statut) VALUES (?, ?, 'DOWN')", 
                    (nom_lecteur, adresse_ip))
        conn.commit()
        conn.close()

    def findStatut(self):
        """Vérifie le statut des lecteurs via ping"""
        conn = self._getDBConnection()
        try:
            ip_adresse = conn.execute('SELECT DISTINCT adresse_ip FROM lecteur').fetchall()
            for ip in ip_adresse:
                ip_t = ip[0]
                delay = ping(ip_t, timeout=4)

                if delay is not None and delay is not False:
                    conn.execute("UPDATE lecteur SET statut = 'UP' WHERE adresse_ip = ?", (ip_t,))
                else:
                    conn.execute("UPDATE lecteur SET statut = 'DOWN' WHERE adresse_ip = ?", (ip_t,))
            
            conn.commit()
            print("Programme exécuté à la perfection")
        except Exception as e:
            print(f"Erreur {e} dans findStatut")
        finally:
            conn.close()

    def Sync(self, adresse_ip):
        """Synchronise un lecteur donné"""
        try:
            conn = self._getDBConnection()
            cmd = ['sudo', 'tailscale', 'up', '--reset']
            subprocess.run(cmd, capture_output=True)

            delay = ping(adresse_ip, timeout=4)

            if delay is not None and delay is not False:
                conn.execute("UPDATE lecteur SET statut = 'UP' WHERE adresse_ip = ?", (adresse_ip,))
                conn.commit()
            else:
                print('Erreur ping')
            
            conn.close()
        except Exception as e:
            print(f'Erreur {e} dans Sync')

    def SyncAll(self):
        """Synchronise tous les lecteurs"""
        try:
            conn = self._getDBConnection()
            cmd = ['sudo', 'tailscale', 'up', '--reset']
            subprocess.run(cmd, capture_output=True)

            ips = conn.execute("SELECT adresse_ip FROM lecteur").fetchall()

            for ip_row in ips:
                ip = ip_row[0]
                delay = ping(ip, timeout=4)

                if delay is not None and delay is not False:
                    conn.execute("UPDATE lecteur SET statut = 'UP' WHERE adresse_ip = ?", (ip,))
                else:
                    print(f'Erreur ping pour {ip}')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f'Erreur {e} dans SyncAll')

    def pullMP3toPlayers(self):
        """Push les fichiers MP3 vers les lecteurs via rsync"""
        try:
            conn = self._getDBConnection()
            dir_path = "/home/servermysky/MYSKY_SAE/PagesCodes/Sae_V2/app/static/audio"
            hosts = conn.execute("SELECT nom_lecteur, adresse_ip FROM lecteur").fetchall()

            for nom_lecteur, adresse_ip in hosts:
                cmd = [
                    "sudo",
                    "rsync", "-avz", "--progress",
                    f"{dir_path}/",
                    f"{nom_lecteur}@{adresse_ip}:/home/test/Musique"
                ]

                res = subprocess.run(cmd, capture_output=True, text=True)

                if res.returncode == 0:
                    # tout va bien
                    update_mpd = ["ssh", f"{nom_lecteur}@{adresse_ip}", "mpc -p 6601 update"]
                    subprocess.run(update_mpd, capture_output=True)

            conn.close()
        except Exception as e:
            print(f"Erreur {e} dans pullMP3toPlayers")

    def Pullm3uToPlayers(self):
        """Push les playlists M3U vers les lecteurs"""
        try:
            conn = self._getDBConnection()
            hosts = conn.execute('SELECT DISTINCT nom_lecteur, adresse_ip FROM lecteur').fetchall()
            f = "/home/servermysky/MYSKY_SAE/PagesCodes/Sae_V2/app/static/playlists"

            for nom_lecteur, adresse_ip in hosts:
                cmd = [
                    "sudo",
                    "rsync", "-avz", "--progress",
                    f"{f}/",
                    f"{nom_lecteur}@{adresse_ip}:/home/test/playlists"
                ]
                subprocess.run(cmd, capture_output=True)

                update_mpd = ["ssh", f"{nom_lecteur}@{adresse_ip}", "mpc -p 6601 update"]
                subprocess.run(update_mpd, capture_output=True)

            conn.close()
        except Exception as e:
            print(f"Erreur {e} dans Pullm3uToPlayers")

    def playm3ubydayandtimestamp(self):
        """Joue les playlists selon le jour et l'heure"""
        try:
            client = MPDClient()
            jours = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]

            get = requests.get(f"http://127.0.0.1:5000/api/v1/playlists")
            json_data = get.json()

            now = datetime.now()
            jour_actuel = jours[now.weekday()]
            date_et_temps = now.strftime("%Y-%m-%d %H:%M")

            conn = self._getDBConnection()
            ips = conn.execute("SELECT adresse_ip FROM lecteur").fetchall()
            conn.close()

            for file in json_data.get('playlists', []):
                date_heure = file.get('date_heure_diffusion')
                jour_semaine = file.get('jour_semaine')

                jouer_playlist = False

                if date_heure == date_et_temps:
                    jouer_playlist = True
                elif jour_semaine == jour_actuel:
                    jouer_playlist = True



                if jouer_playlist:
                    name = file.get("nom_playlist")
                    for ip in ips:
                        ip = ip[0]
                        client.connect(ip, 6600)
                        client.clear()
                        client.load(name)
                        client.play()
                        client.disconnect()

        except Exception as e:
            print(f"Erreur {e} dans la méthode playm3ubydayandtimestamp")

    def Ad(self, mp3):
        """
        Pause la playlist, joue la pub, puis reprend la playlist
        """
        try:
            client = MPDClient()
            conn = self._getDBConnection()
            ips = conn.execute("SELECT adresse_ip FROM lecteur WHERE statut = 'UP'").fetchall()

            for ip_row in ips:
                ip = ip_row[0]
                
                try:
                    client.connect(ip, 6601)
                    status = client.status()
                    
                    # Sauvegarder la position actuelle
                    playlist_pos = int(status.get('song', 0))
                    playlist_state = status.get('state', 'stop')

                    # Pause si en lecture
                    if playlist_state == "play":
                        client.pause(1)
                    
                    # Ajouter et jouer la pub
                    client.add(mp3)
                    playlist_length = int(client.status()['playlistlength'])
                    client.play(playlist_length - 1)  # Jouer le dernier ajouté

                    # Attendre la durée de la pub
                    current = client.currentsong()
                    duree = int(current.get("time", "0").split(":")[0]) if "time" in current else 45
                    time.sleep(duree + 1)

                    # Supprimer la pub de la playlist
                    client.delete(playlist_length - 1)

                    # Reprendre la musique
                    if playlist_state == "play":
                        client.play(playlist_pos)
                    
                    client.close()
                    client.disconnect()
                    
                except Exception as e:
                    print(f"Erreur connexion MPD sur {ip}: {e}")
                    try:
                        client.close()
                        client.disconnect()
                    except:
                        pass

            conn.close()
        except Exception as e:
            print(f"Erreur {e} dans Ad")

    def WhatPlayerPlaying(self):
        """
        Retourne les informations sur ce qui joue
        """
        try:
            client = MPDClient()
            conn = self._getDBConnection()
            ips = conn.execute("""
                SELECT l.adresse_ip, lo.ville 
                FROM lecteur l 
                JOIN localisation lo USING(id_localisation)
                WHERE l.statut = 'UP'
                LIMIT 1
            """).fetchone()
            
            if not ips:
                return None
            
            ip, localisation = ips[0], ips[1]
            
            try:
                client.connect(ip, 6601)
                status = client.status()
                song = client.currentsong()
                
                elapsed = int(float(status.get("elapsed", 0)))
                duration_str = song.get("time", "0")
                duration = int(duration_str.split(":")[0]) if ":" in duration_str else int(duration_str)
                file_path = song.get("file", "Inconnu")
                name = song.get("title", song.get("file", "Inconnu"))

                client.close()
                client.disconnect()
                
                conn.close()

                return {
                    "ip": ip,
                    "localisation": localisation,
                    "file": file_path,
                    "name": name,
                    "elapsed": elapsed,
                    "duration": duration
                }
            except Exception as e:
                print(f"Erreur connexion MPD: {e}")
                try:
                    client.close()
                    client.disconnect()
                except:
                    pass
                conn.close()
                return None
                
        except Exception as e:
            print(f"Erreur {e} dans WhatPlayerPlaying")
            return None

    def getAllPlayer(self):
        """Récupère tous les lecteurs"""
        try:
            players = []
            conn = self._getDBConnection()
            hosts = conn.execute("SELECT * FROM lecteur").fetchall()

            for host in hosts:
                players.append(dict(host))

            conn.close()
            return players
        except Exception as e:
            print(f"Erreur {e} dans getAllPlayer")
            return []

    def getAllPlayerWithTheirLocalisation(self):
        """Récupère tous les lecteurs avec leur localisation"""
        try:
            players = []
            conn = self._getDBConnection()
            hosts = conn.execute("SELECT * FROM lecteur JOIN localisation USING(id_localisation)").fetchall()

            for host in hosts:
                players.append(dict(host))

            conn.close()
            return players
        except Exception as e:
            print(f"Erreur {e} dans getAllPlayerWithTheirLocalisation")
            return []

    def findByIP(self, adresse_ip):
        """Trouve un lecteur par IP"""
        try:
            conn = self._getDBConnection()
            host = conn.execute("SELECT * FROM lecteur WHERE adresse_ip = ?", (adresse_ip,)).fetchone()
            conn.close()
            
            if host:
                return lecteur(dict(host))
            return None
        except Exception as e:
            print(f"Erreur {e} dans findByIP")
            return None

    def findByEmplacement(self, emplacement):
        """Trouve un lecteur par emplacement"""
        try:
            conn = self._getDBConnection()
            hosts = conn.execute("""
                SELECT * FROM lecteur l 
                JOIN localisation lo USING(id_localisation) 
                WHERE ville = ?
            """, (emplacement,)).fetchall()
            conn.close()
            
            return [lecteur(dict(host)) for host in hosts]
        except Exception as e:
            print(f"Erreur {e} dans findByEmplacement")
            return []

    def getAllUp(self):
        """Retourne tous les lecteurs UP"""
        try:
            up = []
            conn = self._getDBConnection()
            hosts = conn.execute("SELECT DISTINCT * FROM lecteur WHERE statut = 'UP'").fetchall()

            for host in hosts:
                up.append(dict(host))

            conn.close()
            return up
        except Exception as e:
            print(f"Erreur {e} dans getAllUp")
            return []

    def getAllDown(self):
        """Retourne tous les lecteurs DOWN"""
        try:
            down = []
            conn = self._getDBConnection()
            hosts = conn.execute("SELECT DISTINCT * FROM lecteur WHERE statut = 'DOWN' OR statut = 'KO'").fetchall()

            for host in hosts:
                down.append(dict(host))

            conn.close()
            return down
        except Exception as e:
            print(f"Erreur {e} dans getAllDown")
            return []
