import sqlite3
from app import app
from app.models.User import User
from app.models.UserDAOInterface import UserDAOInterface

import bcrypt # pip install bcrypt --break-system-packages


class UserSqliteDAO(UserDAOInterface):
	"""
	User data access object dédié à SQLite
	"""

	def __init__(self):
		self.databasename = app.root_path + '/database.db'
		self._initTable()

	def _getDbConnection(self):
		""" connection à la base de données. Retourne l'objet connection """
		conn = sqlite3.connect(self.databasename)
		conn.row_factory = sqlite3.Row
		return conn

	def _initTable(self):
		conn = self._getDbConnection()
		conn.execute('''
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY,
				username TEXT UNIQUE NOT NULL,
				password TEXT NOT NULL,
				role TEXT NOT NULL DEFAULT 'lecteur' 
			)
		''')
		conn.commit()
		conn.close()
	
	def _generatePwdHash(self, password):
		password_bytes = password.encode('utf-8')
		hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
		password_hash = hashed_bytes.decode('utf-8')
		return password_hash

	def createUser(self, username, password, role='lecteur'):
		conn = self._getDbConnection()
		hashed_password = self._generatePwdHash(password)
		try:
			conn.execute(
				"INSERT INTO users (username, password, role) VALUES (:username, :password, :role)",
				{"username":username, "password":hashed_password, "role":role}
			)
			conn.commit()
		except sqlite3.IntegrityError:
			return False # erreur lors de la création, sans doute que l'utilisateur existe déjà
		finally:
			conn.close()
			return True # création réussie

	def findByUsername(self, username):
		"""
		Récupère un utilisateur par son username
		Cette version est faite pour rendre l'instance, donc sans mot de passe
		"""
		conn = self._getDbConnection()
		user = conn.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
		conn.close()
		if user:
			user = User(user)
		return user
		
	def verifyUser(self, username, password):
		"""
		Vérifie les informations de connexion et retourne l'instance de l'utilisateur ou None
		Cette version est faite pour comparer les mots de passe chiffrés
		"""
		conn = self._getDbConnection()
		user = conn.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
		conn.close()
		
		if user:
			# Check password using bcrypt
			password_bytes = password.encode('utf-8')
			stored_hash_bytes = user['password'].encode('utf-8')
			
			if bcrypt.checkpw(password_bytes, stored_hash_bytes):
				# Return a dictionary of the necessary data for the session
				return User(user)
				
		return None # Login failed

	def findAll(self):
		""" trouve tous les users """
		conn = self._getDbConnection()
		users = conn.execute('SELECT * FROM users').fetchall()
		instances = list()
		for user in users:
			instances.append(User(dict(user)))
		conn.close()
		return instances
	
	def deleteByUsername(self, username):
		conn = self._getDbConnection()
		res = conn.execute("DELETE FROM users WHERE username = ?", (username,))
		conn.commit()
		conn.close()
		return True