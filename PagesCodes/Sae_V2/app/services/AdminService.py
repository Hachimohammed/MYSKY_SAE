from app.models.lecteurDAO import lecteurDAO
from app.models.UserDAO import UserSqliteDAO

class AdminService:
    """Service admin avec correction des méthodes"""

    def __init__(self):
        self.ld = lecteurDAO()
        self.us = UserSqliteDAO()

    def findPlayer(self):
        self.ld.findPlayer()

    def findStatut(self):
        self.ld.findStatut()

    def Sync(self, adresse_ip):
        self.ld.Sync(adresse_ip) 

    def SyncAll(self):
        self.ld.SyncAll()

    def pullMP3toplayers(self):
        self.ld.pullMP3toPlayers()

    def Pullm3uToPlayers(self):
        self.ld.Pullm3uToPlayers()

    def playm3ubydayandtimestamp(self):
        self.ld.playm3ubydayandtimestamp()

    def Ad(self, mp3):
        """CORRECTION: passer le paramètre mp3"""
        self.ld.Ad(mp3)

    def getAllPlayer(self):
        return self.ld.getAllPlayer()
    
    def getAllPlayerWithTheirLocalisation(self):
        return self.ld.getAllPlayerWithTheirLocalisation()
    
    def getAllPlayerLen(self):
        return len(self.ld.getAllPlayer())
    
    def findByIP(self, adresse_ip):
        return self.ld.findByIP(adresse_ip)
    
    def findByLocalisation(self, emplacement):
        """CORRECTION: ajouter paramètre emplacement"""
        return self.ld.findByEmplacement(emplacement)
    
    def getAllUp(self):
        return self.ld.getAllUp()
    
    def getAllDown(self):
        return self.ld.getAllDown()
    
    def lenGetAllDown(self):
        return len(self.ld.getAllDown())
    
    def lenGetAllUp(self):
        return len(self.ld.getAllUp())
    
    def WhatPlayerPlaying(self):
        """CORRECTION: retourner le résultat"""
        return self.ld.WhatPlayerPlaying()
    
    def addUser(self, prenom, nom, mail, mot_de_passe, id_groupe):
        """CORRECTION: ordre des paramètres"""
        self.us.addUser(prenom, nom, mail, mot_de_passe, id_groupe)

    def getAllUsers(self):
        return self.us.getAllUsers()
    
    def deleteUser(self, user_id):
        self.us.deleteUser(user_id)