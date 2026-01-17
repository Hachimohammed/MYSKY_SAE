from app.models.BDDao import DatabaseInit as BDDao
import sqlite3
from app import app
from app.models.User import User
import bcrypt

class UserSqliteDAO:

    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
    
    def _getDbConnection(self):
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON;") 
        conn.row_factory = sqlite3.Row
        return conn

    def _generatePwdHash(self, mot_de_passe):
        mot_de_passe_bits = mot_de_passe.encode('utf-8')
        bits_hachage = bcrypt.hashpw(mot_de_passe_bits, bcrypt.gensalt())
        mot_de_passe_hache = bits_hachage.decode('utf-8')
        return mot_de_passe_hache

    def addUser(self, prenom, nom, email, mot_de_passe, id_groupe):

        conn = self._getDbConnection()
        mdp_hache=self._generatePwdHash(mot_de_passe)

        try:
            conn.execute(
                "INSERT INTO Utilisateur (nom, prenom, email, mdp, id_Groupe)VALUES (:nom, :prenom, :email, :mdp, :id_Groupe)", 
                {"prenom":prenom, "nom":nom, "email":email, "mdp":mdp_hache, "id_Groupe":id_groupe}
            )
            conn.commit()

        except sqlite3.IntegrityError:
            return False
        
        finally:
            conn.close()
            return True

    def findByEmail(self, email):
        """
		Récupère un utilisateur par son username
		Cette version est faite pour rendre l'instance, donc sans mot de passe
		"""
        conn = self._getDbConnection()
        user = conn.execute("SELECT * FROM Utilisateur WHERE email = :email", {"email": email}).fetchone()
        conn.close()
        if user:
            user = User(user)
        return user

    def verifyUser(self, email, mdp):
        conn = self._getDbConnection()
        user = conn.execute("SELECT * FROM Utilisateur JOIN Groupe_Role USING(id_Groupe) WHERE email = :email", {"email": email}).fetchone()
        conn.close()
		
        if user:
			# verif mot de passe et comparaison
            mdp_bits = mdp.encode('utf-8')
            bits_haches_stocke = user['mdp'].encode('utf-8')
			
            if bcrypt.checkpw(mdp_bits, bits_haches_stocke):
				# dictionnaire pour les données de la session dans login controller
                return User(user)
				
        return None # echec de connexion

    def findGroupes(self):
        conn = self._getDbConnection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_Groupe, nom_groupe FROM Groupe_Role")
        groupes = cursor.fetchall()
        conn.close()
        instances_groupes=list()
        for g in groupes:
            instances_groupes.append(g)
        return instances_groupes

    def findAllUsers(self):
        conn = self._getDbConnection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                u.id_utilisateur,
                u.prenom,
                u.nom,
                u.email,
                u.id_Groupe,
                g.nom_groupe
            FROM Utilisateur u
            JOIN Groupe_Role g ON u.id_groupe = g.id_groupe
        """)

        users = cursor.fetchall()
        conn.close()
        instances_users=list()
        for user in users:
            instances_users.append(User(dict(user)))
        return instances_users

    def deleteByEmail(self, email):
        conn = self._getDbConnection()
        res = conn.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return True

    def deleteUser(self,email):
        conn = self._getDbConnection()
        cursor = conn.cursor()
        groupe=cursor.execute(
            "SELECT nom_groupe FROM Utilisateur JOIN Groupe_Role USING(id_Groupe) WHERE email = ?",
            (email,)
        )

        if groupe=="ADMIN":
            conn.close()
            return 0
        #un admin ne peut supprimer un autre admin
        
        cursor.execute(
            "DELETE FROM Utilisateur WHERE email = ?",
            (email,)
        )

        conn.commit()
        conn.close()




