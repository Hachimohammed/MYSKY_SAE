class PlaylistDAOInterface:
    """Interface DAO pour les playlists M3U"""
    
    def create(self, nom_playlist, chemin_fichier_m3u, duree_total, id_planning, jour_semaine):
        """Crée une nouvelle playlist M3U"""
        pass
    
    def getById(self, id_playlist):
        """Récupère une playlist par son ID"""
        pass
    
    def getAll(self):
        """Récupère toutes les playlists"""
        pass
    
    def getByPlanning(self, id_planning):
        """Récupère les playlists d'un planning"""
        pass
    
    def getByDay(self, jour_semaine):
        """Récupère la playlist d'un jour spécifique"""
        pass
    
    def update(self, id_playlist, nom_playlist, duree_total):
        """Met à jour une playlist"""
        pass
    
    def delete(self, id_playlist):
        """Supprime une playlist"""
        pass
    
    def addAudioFile(self, id_playlist, id_fichier):
        """Ajoute un fichier audio à une playlist"""
        pass
    
    def removeAudioFile(self, id_playlist, id_fichier):
        """Retire un fichier audio d'une playlist"""
        pass
    
    def getAudioFiles(self, id_playlist):
        """Récupère tous les fichiers audio d'une playlist"""
        pass
    
    def generateM3U(self, id_playlist):
        """Génère le fichier M3U physique pour une playlist"""
        pass
    
    def generateM3UForDay(self, jour_semaine, id_planning):
        """Génère une playlist M3U pour un jour de la semaine"""
        pass
    
    def generateWeeklyM3U(self, id_planning):
        """Génère toutes les playlists M3U de la semaine"""
        pass
    
    def assignToPlayer(self, id_playlist, id_lecteur, date_diffusion):
        """Assigne une playlist à un lecteur (table joue_dans)"""
        pass
    
    def getPlayersForPlaylist(self, id_playlist):
        """Récupère les lecteurs assignés à une playlist"""
        pass
    
    def getDownloadUrl(self, id_playlist):
        """Génère l'URL de téléchargement du fichier M3U pour l'API"""
        pass