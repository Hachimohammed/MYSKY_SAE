class UserDAOInterface:
	"""Interface pour le DAO user"""
	
	def createUser(self, username, password, role='lecteur'):
		""" crée un utilisateur """
		pass

	def findByUsername(self, username):
		""" trouve un utilisateur par son username """
		pass

	def verifyUser(self, username, password):
		"""
		Vérifie les informations de connexion et retourne l'instance de l'utilisateur ou None
		"""
		pass

	def findAll(self):
		""" trouve tous les utilisateurs """
		pass

	def deleteByUsername(self, username):
		pass