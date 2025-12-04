from app.models.UserDAO import UserSqliteDAO as UserDAO

class UserService():
	"""
	Classe dédiée à la logique des utilisateurs
	"""
	def __init__(self):
		self.udao = UserDAO()

	def getUserByUsername(self, username):
		res = self.udao.findByUsername(username)
		if type(res) is not list: 
			res = [res] 
		return res

	def getUsers(self):
		return self.udao.findAll()
	
	def signin(self, username, password):
		return self.udao.createUser(username, password)

	def login(self, username, password):
		return self.udao.verifyUser(username, password)
	
	def deleteUser(self, username):
		return self.udao.deleteByUsername(username)