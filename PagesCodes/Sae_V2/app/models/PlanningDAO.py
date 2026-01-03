import sqlite3
from datetime import datetime, timedelta
from app import app
from app.models.Planning import Planning
from app.models.PlanningDAOInterface import PlanningDAOInterface
from app.models.PlaylistDAO import PlaylistDAO

class PlanningDAO(PlanningDAOInterface):
    """DAO pour la gestion des plannings hebdomadaires"""
    
    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
        self.playlist_dao = PlaylistDAO()
    
    def _getDbConnection(self):
        """Obtient une connexion à la base de données"""
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn
    
    def create(self, nom_planning, date_debut, date_fin):
        """Crée un nouveau planning"""
        try:
            conn = self._getDbConnection()
            date_creation = datetime.now().isoformat()
            
            cursor = conn.execute("""
                INSERT INTO planning (nom_planning, date_debut, date_fin, actif_ou_non)
                VALUES (?, ?, ?, 1)
            """, (nom_planning, date_debut, date_fin))
            
            id_planning = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return Planning({
                'id_planning': id_planning,
                'nom_planning': nom_planning,
                'date_debut': date_debut,
                'date_fin': date_fin,
                'actif_ou_non': 1,
                'date_creation': date_creation
            })
        except Exception as e:
            print(f"Erreur dans create: {e}")
            return None
    
    def getById(self, id_planning):
        """Récupère un planning par son ID"""
        try:
            conn = self._getDbConnection()
            row = conn.execute(
                "SELECT * FROM planning WHERE id_planning = ?",
                (id_planning,)
            ).fetchone()
            conn.close()
            
            if row:
                return Planning(dict(row))
            return None
        except Exception as e:
            print(f"Erreur dans getById: {e}")
            return None
    
    def getAll(self):
        """Récupère tous les plannings"""
        try:
            conn = self._getDbConnection()
            rows = conn.execute("""
                SELECT * FROM planning
                ORDER BY date_debut DESC
            """).fetchall()
            conn.close()
            
            return [Planning(dict(row)) for row in rows]
        except Exception as e:
            print(f"Erreur dans getAll: {e}")
            return []
    
    def getActive(self):
        """Récupère uniquement les plannings actifs"""
        try:
            conn = self._getDbConnection()
            rows = conn.execute("""
                SELECT * FROM planning
                WHERE actif_ou_non = 1
                ORDER BY date_debut DESC
            """).fetchall()
            conn.close()
            
            return [Planning(dict(row)) for row in rows]
        except Exception as e:
            print(f"Erreur dans getActive: {e}")
            return []
    
    def getCurrent(self):
        """Récupère le planning actif en cours (selon la date)"""
        try:
            conn = self._getDbConnection()
            today = datetime.now().date().isoformat()
            
            row = conn.execute("""
                SELECT * FROM planning
                WHERE actif_ou_non = 1
                AND date_debut <= ?
                AND date_fin >= ?
                ORDER BY date_debut DESC
                LIMIT 1
            """, (today, today)).fetchone()
            conn.close()
            
            if row:
                return Planning(dict(row))
            return None
        except Exception as e:
            print(f"Erreur dans getCurrent: {e}")
            return None
    
    def update(self, id_planning, nom_planning, date_debut, date_fin):
        """Met à jour un planning"""
        try:
            conn = self._getDbConnection()
            conn.execute("""
                UPDATE planning
                SET nom_planning = ?, date_debut = ?, date_fin = ?
                WHERE id_planning = ?
            """, (nom_planning, date_debut, date_fin, id_planning))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur dans update: {e}")
            return False
    
    def delete(self, id_planning):
        """Supprime un planning"""
        try:
            conn = self._getDbConnection()
            
            conn.execute("DELETE FROM playlist WHERE id_planning = ?", (id_planning,))
            
            conn.execute("DELETE FROM planning WHERE id_planning = ?", (id_planning,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur dans delete: {e}")
            return False
    
    def setActive(self, id_planning, actif):
        """Active ou désactive un planning"""
        try:
            conn = self._getDbConnection()
            conn.execute("""
                UPDATE planning
                SET actif_ou_non = ?
                WHERE id_planning = ?
            """, (1 if actif else 0, id_planning))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur dans setActive: {e}")
            return False
    
    def getPlaylists(self, id_planning):
        """Récupère toutes les playlists d'un planning"""
        try:
            return self.playlist_dao.getByPlanning(id_planning)
        except Exception as e:
            print(f"Erreur dans getPlaylists: {e}")
            return []
    
    def generateFullWeek(self, id_planning):
        """Génère toutes les playlists pour une semaine complète"""
        try:
            return self.playlist_dao.generateWeeklyM3U(id_planning)
        except Exception as e:
            print(f"Erreur dans generateFullWeek: {e}")
            return []
    
    def duplicatePlanning(self, id_planning, nouvelle_date_debut, nouvelle_date_fin):
        """Duplique un planning existant avec de nouvelles dates"""
        try:
            
            planning_original = self.getById(id_planning)
            if not planning_original:
                return None
            
            
            nouveau_nom = f"{planning_original.nom_planning}_copie_{datetime.now().strftime('%Y%m%d')}"
            nouveau_planning = self.create(nouveau_nom, nouvelle_date_debut, nouvelle_date_fin)
            
            if not nouveau_planning:
                return None
            
     
            playlists_originales = self.getPlaylists(id_planning)
            for playlist in playlists_originales:
                
                nouveau_nom_playlist = f"{playlist.nom_playlist}_copie"
                chemin_m3u = playlist.chemin_fichier_m3u.replace('.m3u', '_copie.m3u')
                
                nouvelle_playlist = self.playlist_dao.create(
                    nouveau_nom_playlist,
                    chemin_m3u,
                    playlist.duree_total,
                    nouveau_planning.id_planning,
                    playlist.jour_semaine
                )
                
                if nouvelle_playlist:
                  
                    audio_files = self.playlist_dao.getAudioFiles(playlist.id_playlist)
                    for audio in audio_files:
                        self.playlist_dao.addAudioFile(nouvelle_playlist.id_playlist, audio.id_fichier)
                    
                    
                    self.playlist_dao.generateM3U(nouvelle_playlist.id_playlist)
            
            return nouveau_planning
        except Exception as e:
            print(f"Erreur dans duplicatePlanning: {e}")
            return None