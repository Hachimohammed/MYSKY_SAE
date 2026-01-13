from app.models.lecteurDAO import lecteurDAO
from app.models.lecteurDAOInterface import lecteurDAOInterface
from app.models.UserDAO import UserSqliteDAO

class AdminService():

    def __init__(self):
        self.ld = lecteurDAO(lecteurDAOInterface)
        self.us = UserSqliteDAO()

    def findPlayer(self):
        self.ld.findPlayer()

    def findStatut(self):
        self.ld.findStatut()

    def Sync(self,adresse_ip):
        self.ld.Sync(adresse_ip) 

    def SyncAll(self):
        self.ld.SyncAll()

    def pullMP3toplayers(self):
        self.ld.pullMP3toPlayers()

    def Pullm3uToPlayers(self):
        self.ld.Pullm3uToPlayers()

    def playm3ubydayandtimestamp(self):
        self.ld.playm3ubydayandtimestamp()

    def Ad(self,mp3):
        self.ld.Ad()

    def getAllPlayer(self):
        return self.ld.getAllPlayer()
    
    def findByIP(self,adresse_ip):
        return self.ld.findByIP()
    
    def getAllUp(self):
        return self.ld.getAllUp()
    
    def getAllDown(self):
        return self.ld.getAllDown()
    
    def addUser(prenom, nom, mail, mot_de_passe, id_groupe, self):
        self.us.addUser(prenom, nom, mail, mot_de_passe, id_groupe)

    def getAllUsers(self):
        return self.us.getAllUsers()
    
    def deleteUser(self,user_id):
        self.us.deleteUser(user_id)
    

