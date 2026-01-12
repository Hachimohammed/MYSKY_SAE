from app.models.UserDAO import UserSqliteDAO as UserDAO
import sqlite3
import bcrypt
from flask import current_app

class UserService:
    def _getDbconnection(self):
       
        conn = sqlite3.connect(current_app.root_path + '/musicapp.db')
        conn.row_factory = sqlite3.Row
        return conn

    def login(self, email, password):
        conn = self._getDbconnection()
        try:
            
            query = """
                SELECT u.*, g.nom_groupe as role 
                FROM Utilisateur u
                JOIN Groupe_Role g ON u.id_Groupe = g.id_Groupe
                WHERE u.email = ?
            """
            user = conn.execute(query, (email,)).fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['mdp'].encode('utf-8')):
                return user
            return None
        finally:
            conn.close()