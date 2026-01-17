from app.models.UserDAO import UserSqliteDAO as UserDAO
from flask import current_app

class UserService:

    def __init__(self):
        self.udao=UserDAO()

    def getUserByEmail(self, email):
        res = self.udao.findByEmail(email)
        if type(res) is not list: 
            res = [res] 
        return res

    def signin(self, prenom, nom, email, mot_de_passe, id_groupe):
        return self.udao.addUser(prenom, nom, email, mot_de_passe, id_groupe)

    def login(self, email, password):
        return self.udao.verifyUser(email, password)
    
    def getAllUsers(self):
        return self.udao.findAllUsers()
    
    def deleteUser(self, email):
        return self.udao.deleteByEmail(email)
    
    def getAllGroupes(self):
        return self.udao.findGroupes()