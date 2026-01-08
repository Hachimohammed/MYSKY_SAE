from app.models.PlaylistDAO import PlaylistDAO
from datetime import datetime
import os

class PlaylistService:
    """
    Service contenant TOUTE la logique métier des playlists
    """
    
    def __init__(self):
        self.playlist_dao = PlaylistDAO()
    
    # ==================== MÉTHODES DE BASE ====================
    
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
    
    # ==================== LOGIQUE MÉTIER AVANCÉE ====================
    
    def getPlaylistStatistics(self, id_playlist):
        """
        Récupère les statistiques d'une playlist
        Agrège plusieurs informations
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
    
    # ==================== ORCHESTRATION COMPLEXE ====================
    
    def generateWeekPlaylistsWithOrder(self, id_planning, audio_service, app_root_path, use_http_urls=True):
        """
        LOGIQUE MÉTIER COMPLÈTE : Génère toutes les playlists de la semaine en respectant l'ordre sauvegardé
        
        Cette méthode orchestre :
        - Chargement de l'ordre des fichiers (via AudioFileService)
        - Création des playlists pour chaque jour
        - Ajout des fichiers dans l'ordre
        - Génération des fichiers M3U
        
        Retourne: (playlists_created, errors)
        """
        jours = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
        playlists_created = []
        errors = []
        
        ordre_folder = os.path.join(app_root_path, 'static', 'ordre')
        
        for jour in jours:
            try:
                # Charger les fichiers ordonnés via AudioFileService
                fichiers_ordonnes = audio_service.loadPlaybackOrder(jour, ordre_folder)
                
                if not fichiers_ordonnes:
                    print(f"⚠️ Aucun fichier pour {jour}")
                    continue
                
                # Créer la playlist
                nom_playlist = f"Playlist_{jour}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                chemin_m3u = os.path.join(app_root_path, 'static', 'playlists', f"{nom_playlist}.m3u")
                duree_totale = sum(f.duree for f in fichiers_ordonnes if f.duree)
                
                playlist = self.createPlaylist(
                    nom_playlist=nom_playlist,
                    chemin_fichier_m3u=chemin_m3u,
                    duree_total=duree_totale,
                    id_planning=id_planning,
                    jour_semaine=jour
                )
                
                if not playlist:
                    error_msg = f"Erreur création playlist pour {jour}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
                    continue
                
                # Ajouter les fichiers dans l'ordre
                for ordre, fichier in enumerate(fichiers_ordonnes, start=1):
                    self.addAudioWithOrder(playlist.id_playlist, fichier.id_fichier, ordre)
                
                # Générer le fichier M3U
                if self.generateM3UFile(playlist.id_playlist, use_http_urls):
                    playlists_created.append(playlist)
                    print(f"✅ Playlist générée pour {jour} avec {len(fichiers_ordonnes)} fichiers")
                else:
                    error_msg = f"Erreur génération M3U pour {jour}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
                    
            except Exception as e:
                error_msg = f"Erreur lors de la génération de la playlist {jour}: {str(e)}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
        
        return playlists_created, errors
    
    def deletePlaylistWithPhysicalFile(self, id_playlist):
        """
        Supprime une playlist ET son fichier M3U physique
        Retourne: (success, error_message)
        """
        playlist = self.getPlaylistById(id_playlist)
        
        if not playlist:
            return False, 'Playlist introuvable'
        
        # Supprimer le fichier M3U physique
        if playlist.chemin_fichier_m3u and os.path.exists(playlist.chemin_fichier_m3u):
            try:
                os.remove(playlist.chemin_fichier_m3u)
                print(f"✅ Fichier M3U supprimé: {playlist.chemin_fichier_m3u}")
            except Exception as e:
                print(f"❌ Erreur suppression fichier M3U: {e}")
        
        # Supprimer de la BDD
        if self.deletePlaylist(id_playlist):
            return True, None
        else:
            return False, 'Erreur suppression BDD'
    
    def formatPlaylistForApi(self, playlist, include_files=False):
        """
        Formate une playlist pour l'API
        """
        data = {
            'id_playlist': playlist.id_playlist,
            'nom_playlist': playlist.nom_playlist,
            'jour_semaine': playlist.jour_semaine,
            'duree_totale': playlist.duree_total,
            'download_m3u_url': f"/api/v1/playlist/download/{playlist.id_playlist}"
        }
        
        if include_files:
            fichiers = self.getPlaylistAudioFiles(playlist.id_playlist)
            data['nombre_fichiers'] = len(fichiers)
            data['fichiers'] = [f.to_dict() for f in fichiers]
        
        return data