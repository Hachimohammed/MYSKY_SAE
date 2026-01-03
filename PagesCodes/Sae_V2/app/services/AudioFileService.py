from app.models.AudioFileDAO import AudioFileDAO

class AudioFileService:
    """
    Classe dédiée à la logique métier des fichiers audio
    """
    
    def __init__(self):
        self.audio_dao = AudioFileDAO()
    
    def getAllAudioFiles(self):
        """Récupère tous les fichiers audio"""
        return self.audio_dao.getAll()
    
    def getAudioFileById(self, id_fichier):
        """Récupère un fichier audio par son ID"""
        return self.audio_dao.getById(id_fichier)
    
    def getAudioFilesByDay(self, jour_semaine):
        """Récupère tous les fichiers audio d'un jour spécifique"""
        return self.audio_dao.getByDay(jour_semaine)
    
    def createAudioFile(self, nom, type_fichier, taille, chemin_fichier, 
                       id_type_contenu=1, duree=None, artiste=None, 
                       album=None, jour_semaine=None, id_utilisateur=None):
        """Crée un nouveau fichier audio"""
        return self.audio_dao.create(nom, type_fichier, taille, chemin_fichier, 
                                     id_type_contenu, duree, artiste, album, 
                                     jour_semaine, id_utilisateur)
    
    def updateAudioFile(self, id_fichier, nom, taille):
        """Met à jour un fichier audio"""
        return self.audio_dao.update(id_fichier, nom, taille)
    
    def deleteAudioFile(self, id_fichier):
        """Supprime un fichier audio"""
        return self.audio_dao.delete(id_fichier)
    
    def deleteAudioFilesByDay(self, jour_semaine):
        """Supprime tous les fichiers d'un jour"""
        return self.audio_dao.deleteByDay(jour_semaine)
    
    def searchAudioFiles(self, keyword):
        """Recherche des fichiers par mot-clé"""
        return self.audio_dao.search(keyword)
    
    def getAudioFilesByUser(self, id_utilisateur):
        """Récupère les fichiers ajoutés par un utilisateur"""
        return self.audio_dao.getByUser(id_utilisateur)
    
    def getAudioFilesByType(self, id_type_contenu):
        """Récupère les fichiers par type de contenu"""
        return self.audio_dao.getByType(id_type_contenu)
    
    def getDayStatistics(self, jour_semaine):
        """Récupère les statistiques d'un jour (durée, taille, nombre)"""
        total_duration = self.audio_dao.getTotalDuration(jour_semaine)
        total_size = self.audio_dao.getTotalSize(jour_semaine)
        count = self.audio_dao.getCount(jour_semaine)
        
        return {
            "jour": jour_semaine,
            "total_duration": total_duration,
            "total_size": total_size,
            "count": count
        }
    
    def getDownloadUrl(self, id_fichier):
        """Génère l'URL de téléchargement"""
        return self.audio_dao.getDownloadUrl(id_fichier)
    
    def addAudioFileToUser(self, id_fichier, id_utilisateur):
        """Associe un fichier à un utilisateur"""
        return self.audio_dao.addToUser(id_fichier, id_utilisateur)