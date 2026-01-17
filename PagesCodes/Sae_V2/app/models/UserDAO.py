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
        conn.execute("PRAGMA foreign_keys = ON")
        mdp_hache = self._generatePwdHash(mot_de_passe)

        try:
            print("Debut insertion bdd")
            conn.execute(
                "INSERT INTO Utilisateur (nom, prenom, email, mdp, id_Groupe) VALUES (?, ?, ?, ?, ?)", 
                (nom, prenom, email, mdp_hache, int(id_groupe))
            )
            print("avt commit")
            conn.commit()
            print("apres commmit")

        except sqlite3.IntegrityError as e:
            print(f" Erreur lors de l'ajout utilisateur: {e}")
            return False
        
        finally:
            conn.close()
            return True

    def findByEmail(self, email):
        """Récupère un utilisateur par son email"""
        conn = self._getDbConnection()
        user = conn.execute(
            "SELECT * FROM Utilisateur JOIN Groupe_Role USING(id_Groupe) WHERE email = ?", 
            (email,)
        ).fetchone()
        conn.close()
        
        if user:
            return User(dict(user))
        return None

    def verifyUser(self, email, mdp):
        conn = self._getDbConnection()
        user = conn.execute(
            "SELECT * FROM Utilisateur JOIN Groupe_Role USING(id_Groupe) WHERE email = ?", 
            (email,)
        ).fetchone()
        conn.close()
		
        if user:
           
            mdp_bits = mdp.encode('utf-8')
            bits_haches_stocke = user['mdp'].encode('utf-8')
			
            if bcrypt.checkpw(mdp_bits, bits_haches_stocke):
                return User(dict(user))
				
        return None

    def findGroupes(self):
        """Retourne les groupes sous forme de liste de tuples (id, nom)"""
        conn = self._getDbConnection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_Groupe, nom_groupe FROM Groupe_Role")
        groupes = cursor.fetchall()
        conn.close()
        
        
        return [(g['id_Groupe'], g['nom_groupe']) for g in groupes]

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
        
        return [User(dict(user)) for user in users]

    def deleteByEmail(self, email):
        conn = self._getDbConnection()
        cursor = conn.cursor()
        
        
        user = cursor.execute(
            "SELECT nom_groupe FROM Utilisateur JOIN Groupe_Role USING(id_Groupe) WHERE email = ?",
            (email,)
        ).fetchone()
        
        if not user:
            conn.close()
            return {"success": False, "message": "Utilisateur introuvable"}
        
        if user['nom_groupe'] == "ADMIN":
            conn.close()
            return {"success": False, "message": "Impossible de supprimer un administrateur"}
        
        
        cursor.execute("DELETE FROM Utilisateur WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Utilisateur supprimé avec succès"}