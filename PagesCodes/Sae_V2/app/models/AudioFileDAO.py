import sqlite3
from datetime import datetime
from app import app
from app.models.AudioFile import AudioFile
from app.models.AudioFileDAOInterface import AudioFileDAOInterface

class AudioFileDAO(AudioFileDAOInterface):
    """DAO pour la gestion des fichiers audio MP3"""
    
    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
    
    def _getDbConnection(self):
        """Obtient une connexion à la base de données"""
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn
    
    def create(self, nom, type_fichier, taille, chemin_fichier, id_type_contenu=1,
               duree=None, artiste=None, album=None, jour_semaine=None, id_utilisateur=None):
        """Crée un nouveau fichier audio en base de données"""
        conn = None
        try:
            conn = self._getDbConnection()
            date_ajout = datetime.now().isoformat()
            
            
            cursor = conn.execute("""
                INSERT INTO Fichier_audio (nom, type_fichier, taille, date_ajout, id_Type_contenu,
                                          chemin_fichier, duree, artiste, album, jour_semaine)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nom, type_fichier, taille, date_ajout, id_type_contenu, 
                  chemin_fichier, duree, artiste, album, jour_semaine))
            
            id_fichier = cursor.lastrowid
            
            
            if id_utilisateur:
                conn.execute("""
                    INSERT OR IGNORE INTO Ajoute (id_utilisateur, id_Fichier_audio, Date_Ajout)
                    VALUES (?, ?, ?)
                """, (id_utilisateur, id_fichier, date_ajout))
            
            
            conn.commit()
            
            return AudioFile({
                'id_Fichier_audio': id_fichier,
                'nom': nom,
                'type_fichier': type_fichier,
                'taille': taille,
                'date_ajout': date_ajout,
                'id_Type_contenu': id_type_contenu,
                'chemin_fichier': chemin_fichier,
                'duree': duree,
                'artiste': artiste,
                'album': album,
                'jour_semaine': jour_semaine
            })
        except Exception as e:
            print(f"Erreur dans create: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            
            if conn:
                conn.close()
    
    def getById(self, id_fichier):
        """Récupère un fichier audio par son ID"""
        conn = None
        try:
            conn = self._getDbConnection()
            row = conn.execute(
                "SELECT * FROM Fichier_audio WHERE id_Fichier_audio = ?",
                (id_fichier,)
            ).fetchone()
            
            if row:
                return AudioFile(dict(row))
            return None
        except Exception as e:
            print(f"Erreur dans getById: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def getAll(self):
        """Récupère tous les fichiers audio"""
        conn = None
        try:
            conn = self._getDbConnection()
            rows = conn.execute("""
                SELECT f.*, t.nom_type
                FROM Fichier_audio f
                LEFT JOIN Type_contenu t ON f.id_Type_contenu = t.id_Type_contenu
                ORDER BY f.date_ajout DESC
            """).fetchall()
            
            return [AudioFile(dict(row)) for row in rows]
        except Exception as e:
            print(f"Erreur dans getAll: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def getByDay(self, jour_semaine):
        """Récupère tous les fichiers audio d'un jour spécifique"""
        conn = None
        try:
            conn = self._getDbConnection()
            jour_upper = jour_semaine.upper()
            
            rows = conn.execute("""
                SELECT * FROM Fichier_audio
                WHERE jour_semaine = ? AND id_Type_contenu = 1
                ORDER BY nom
            """, (jour_upper,)).fetchall()
            
            return [AudioFile(dict(row)) for row in rows]
        except Exception as e:
            print(f"Erreur dans getByDay: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def getByType(self, id_type_contenu):
        """Récupère les fichiers par type de contenu"""
        conn = None
        try:
            conn = self._getDbConnection()
            rows = conn.execute("""
                SELECT * FROM Fichier_audio
                WHERE id_Type_contenu = ?
                ORDER BY date_ajout DESC
            """, (id_type_contenu,)).fetchall()
            
            return [AudioFile(dict(row)) for row in rows]
        except Exception as e:
            print(f"Erreur dans getByType: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def getByUser(self, id_utilisateur):
        """Récupère les fichiers ajoutés par un utilisateur"""
        conn = None
        try:
            conn = self._getDbConnection()
            rows = conn.execute("""
                SELECT f.*
                FROM Fichier_audio f
                INNER JOIN Ajoute a ON f.id_Fichier_audio = a.id_Fichier_audio
                WHERE a.id_utilisateur = ?
                ORDER BY a.Date_Ajout DESC
            """, (id_utilisateur,)).fetchall()
            
            return [AudioFile(dict(row)) for row in rows]
        except Exception as e:
            print(f"Erreur dans getByUser: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def update(self, id_fichier, nom, taille):
        """Met à jour les informations d'un fichier"""
        conn = None
        try:
            conn = self._getDbConnection()
            conn.execute("""
                UPDATE Fichier_audio
                SET nom = ?, taille = ?
                WHERE id_Fichier_audio = ?
            """, (nom, taille, id_fichier))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur dans update: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def delete(self, id_fichier):
        """Supprime un fichier audio"""
        conn = None
        try:
            conn = self._getDbConnection()
            # Supprimer les relations
            conn.execute("DELETE FROM fait_partie_de WHERE id_Fichier_audio = ?", (id_fichier,))
            conn.execute("DELETE FROM Ajoute WHERE id_Fichier_audio = ?", (id_fichier,))
            # Supprimer le fichier
            conn.execute("DELETE FROM Fichier_audio WHERE id_Fichier_audio = ?", (id_fichier,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur dans delete: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def deleteByDay(self, jour_semaine):
        """Supprime tous les fichiers d'un jour"""
        try:
            fichiers = self.getByDay(jour_semaine)
            for fichier in fichiers:
                self.delete(fichier.id_fichier)
            return True
        except Exception as e:
            print(f"Erreur dans deleteByDay: {e}")
            return False
    
    def addToUser(self, id_fichier, id_utilisateur):
        """
        ⚠️ DEPRECATED - Utiliser create() avec id_utilisateur directement
        Associe un fichier à un utilisateur dans la table Ajoute
        """
        conn = None
        try:
            conn = self._getDbConnection()
            date_ajout = datetime.now().isoformat()
            conn.execute("""
                INSERT OR IGNORE INTO Ajoute (id_utilisateur, id_Fichier_audio, Date_Ajout)
                VALUES (?, ?, ?)
            """, (id_utilisateur, id_fichier, date_ajout))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur dans addToUser: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def getTotalDuration(self, jour_semaine):
        """Calcule la durée totale des MP3 d'un jour"""
        try:
            fichiers = self.getByDay(jour_semaine)
            total = sum(f.duree for f in fichiers if f.duree)
            return total
        except Exception as e:
            print(f"Erreur dans getTotalDuration: {e}")
            return 0
    
    def getTotalSize(self, jour_semaine):
        """Calcule la taille totale des MP3 d'un jour"""
        try:
            fichiers = self.getByDay(jour_semaine)
            total = sum(f.taille for f in fichiers if f.taille)
            return total
        except Exception as e:
            print(f"Erreur dans getTotalSize: {e}")
            return 0
    
    def getCount(self, jour_semaine):
        """Compte le nombre de fichiers d'un jour"""
        try:
            fichiers = self.getByDay(jour_semaine)
            return len(fichiers)
        except Exception as e:
            print(f"Erreur dans getCount: {e}")
            return 0
    
    def getDownloadUrl(self, id_fichier):
        """Génère l'URL de téléchargement pour l'API"""
        return f"/api/v1/audio/download/{id_fichier}"
    
    def search(self, keyword):
        """Recherche des fichiers par nom ou artiste"""
        conn = None
        try:
            conn = self._getDbConnection()
            rows = conn.execute("""
                SELECT * FROM Fichier_audio
                WHERE nom LIKE ? OR artiste LIKE ?
                ORDER BY date_ajout DESC
            """, (f"%{keyword}%", f"%{keyword}%")).fetchall()
            
            return [AudioFile(dict(row)) for row in rows]
        except Exception as e:
            print(f"Erreur dans search: {e}")
            return []
        finally:
            if conn:
                conn.close()