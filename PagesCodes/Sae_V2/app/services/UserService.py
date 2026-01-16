from app.models.UserDAO import UserSqliteDAO as UserDAO

class UserService:

    def __init__(self):
        self.udao = UserDAO()

    def getUserByEmail(self, email):
        return self.udao.findByEmail(email)

    def createUser(self, prenom, nom, email, password, id_groupe):
        return self.udao.addUser(prenom, nom, email, password, id_groupe)

    def login(self, email, password):
        return self.udao.verifyUser(email, password)
    
    def getAllUsers(self):
        return self.udao.findAllUsers()
    
    def deleteUser(self, email):
        return self.udao.deleteByEmail(email)
    
    def getAllGroupes(self):
        return self.udao.findGroupes()