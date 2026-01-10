from app.models.BDDao import DatabaseInit as BDDao

class UserSqliteDAO:

    def addUser(prenom, nom, mail, mot_de_passe, id_groupe, self):
        conn = BDDao._getDbConnection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Utilisateur (nom, prenom, email, mdp, id_Groupe)
            VALUES (?, ?, ?, ?, ?)
        """, (prenom, nom, mail, mot_de_passe, id_groupe))

        conn.commit()
        conn.close()


    def getGroupes():
        conn = BDDao._getDbConnection()
        cursor = conn.cursor()

        cursor.execute("SELECT id_Groupe, nom_groupe FROM Groupe_Role")
        groupes = cursor.fetchall()

        conn.close()
        return groupes

    def getAllUsers():
        conn = BDDao._getDbConnection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                u.id_utilisateur,
                u.prenom,
                u.nom,
                u.mail,
                g.nom_groupe
            FROM Utilisateur u
            JOIN Groupe g ON u.id_groupe = g.id_groupe
        """)

        users = cursor.fetchall()
        conn.close()
        return users
    
    def deleteUser(user_id):
        conn = BDDao._getDbConnection()
        cursor = conn.cursor()
        groupe=cursor.execute(
            "SELECT nom_groupe FROM Utilisateur JOIN Groupe_Role USING(id_Groupe) WHERE id_utilisateur = ?",
            (user_id,)
        )

        if groupe=="ADMIN":
            conn.close()
            return 0
        #un admin ne peut supprimer un autre admin
        
        cursor.execute(
            "DELETE FROM Utilisateur WHERE id_utilisateur = ?",
            (user_id,)
        )

        conn.commit()
        conn.close()




