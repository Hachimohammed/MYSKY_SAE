from app.models.PlaylistDAO import PlaylistDAO
from datetime import datetime
import os

class PlaylistService:
    """
    Classe dédiée à la logique métier des playlists
    """
    
    def __init__(self):
        self.playlist_dao = PlaylistDAO()
    
    def getAllPlaylists(self):
        """Récupère toutes les playlists"""
        return self.playlist_dao.getAll()
    
    def getPlaylistById(self, id_playlist):
        """Récupère une playlist par son ID"""
        return self.playlist_dao.getById(id_playlist)
    
    def getPlaylistsByPlanning(self, id_planning):
        """Récupère les playlists d'un planning"""
        return self.playlist_dao.getByPlanning(id_planning)
    
    def getPlaylistByDay(self, jour_semaine):
        """Récupère la playlist d'un jour spécifique"""
        return self.playlist_dao.getByDay(jour_semaine)
    
    def createPlaylist(self, nom_playlist, chemin_fichier_m3u, duree_total=0, id_planning=None, jour_semaine=None):
        """Crée une nouvelle playlist"""
        return self.playlist_dao.create(nom_playlist, chemin_fichier_m3u, duree_total, id_planning, jour_semaine)
    
    def updatePlaylist(self, id_playlist, nom_playlist, duree_total):
        """Met à jour une playlist"""
        return self.playlist_dao.update(id_playlist, nom_playlist, duree_total)
    
    def deletePlaylist(self, id_playlist):
        """Supprime une playlist"""
        return self.playlist_dao.delete(id_playlist)
    
    def addAudioToPlaylist(self, id_playlist, id_fichier):
        """Ajoute un fichier audio à une playlist"""
        return self.playlist_dao.addAudioFile(id_playlist, id_fichier)
    
    def removeAudioFromPlaylist(self, id_playlist, id_fichier):
        """Retire un fichier audio d'une playlist"""
        return self.playlist_dao.removeAudioFile(id_playlist, id_fichier)
    
    def getPlaylistAudioFiles(self, id_playlist):
        """Récupère tous les fichiers audio d'une playlist"""
        return self.playlist_dao.getAudioFiles(id_playlist)
    
    def generateM3UFile(self, id_playlist, use_http_urls=True):
        """Génère le fichier M3U physique pour une playlist"""
        return self.playlist_dao.generateM3U(id_playlist, use_http_urls)
    
    def generateDailyPlaylist(self, jour_semaine, id_planning=None, use_http_urls=True):
        """Génère une playlist M3U pour un jour de la semaine"""
        return self.playlist_dao.generateM3UForDay(jour_semaine, id_planning, use_http_urls)
    
    def generateWeeklyPlaylists(self, id_planning, use_http_urls=True):
        """Génère toutes les playlists M3U de la semaine"""
        return self.playlist_dao.generateWeeklyM3U(id_planning, use_http_urls)
    
    def assignPlaylistToPlayer(self, id_playlist, id_lecteur, date_diffusion):
        """Assigne une playlist à un lecteur"""
        return self.playlist_dao.assignToPlayer(id_playlist, id_lecteur, date_diffusion)
    
    def getPlaylistPlayers(self, id_playlist):
        """Récupère les lecteurs assignés à une playlist"""
        return self.playlist_dao.getPlayersForPlaylist(id_playlist)
    
    def getDownloadUrl(self, id_playlist):
        """Génère l'URL de téléchargement du fichier M3U"""
        return self.playlist_dao.getDownloadUrl(id_playlist)
    
    def addAudioWithOrder(self, id_playlist, id_fichier, ordre):
        """Ajoute un fichier audio à une playlist avec un ordre spécifique"""
        return self.playlist_dao.addAudioFileWithOrder(id_playlist, id_fichier, ordre)
    
    def reorderAudioFiles(self, id_playlist, fichiers_ordonnes):
        """Met à jour l'ordre des fichiers dans une playlist"""
        return self.playlist_dao.updateAudioOrder(id_playlist, fichiers_ordonnes)
    
    def getPlaylistStatistics(self, id_playlist):
        """
        Récupère les statistiques d'une playlist
        Logique métier : agrège plusieurs informations
        """
        playlist = self.getPlaylistById(id_playlist)
        if not playlist:
            return None
        
        audio_files = self.getPlaylistAudioFiles(id_playlist)
        players = self.getPlaylistPlayers(id_playlist)
        
        return {
            "playlist_id": id_playlist,
            "nom": playlist.nom_playlist,
            "duree_totale": playlist.duree_total,
            "nombre_fichiers": len(audio_files),
            "nombre_lecteurs": len(players),
            "jour_semaine": playlist.jour_semaine,
            "id_planning": playlist.id_planning,
            "fichier_m3u": playlist.chemin_fichier_m3u
        }
    
    def validatePlaylistBeforeGeneration(self, id_playlist):
        """
        Valide qu'une playlist peut être générée
        Logique métier de validation
        """
        playlist = self.getPlaylistById(id_playlist)
        if not playlist:
            return False, "Playlist introuvable"
        
        audio_files = self.getPlaylistAudioFiles(id_playlist)
        if not audio_files:
            return False, "La playlist ne contient aucun fichier audio"
        
        # Vérifier que les fichiers existent physiquement
        fichiers_manquants = []
        for audio in audio_files:
            if not os.path.exists(audio.chemin_fichier):
                fichiers_manquants.append(audio.nom)
        
        if fichiers_manquants:
            return False, f"Fichiers manquants : {', '.join(fichiers_manquants)}"
        
        return True, "Playlist valide"
    
    def generateAndValidatePlaylist(self, id_playlist, use_http_urls=True):
        """
        Génère une playlist après validation
        Combine validation et génération
        """
        is_valid, message = self.validatePlaylistBeforeGeneration(id_playlist)
        
        if not is_valid:
            return False, message
        
        success = self.generateM3UFile(id_playlist, use_http_urls)
        
        if success:
            return True, "Playlist générée avec succès"
        else:
            return False, "Erreur lors de la génération du fichier M3U"