class AudioFileDAOInterface:
    """Interface DAO pour les fichiers audio"""
    
    def create(self, nom, type_fichier, taille, chemin_fichier, id_type_contenu, 
               duree, artiste, album, jour_semaine, id_utilisateur):
        """Crée un nouveau fichier audio en base de données"""
        pass
    
    def getById(self, id_fichier):
        """Récupère un fichier audio par son ID"""
        pass
    
    def getAll(self):
        """Récupère tous les fichiers audio"""
        pass
    
    def getByDay(self, jour_semaine):
        """Récupère tous les fichiers audio d'un jour spécifique"""
        pass
    
    def getByType(self, id_type_contenu):
        """Récupère les fichiers par type de contenu (MUSIQUE, PUB, ANNONCE)"""
        pass
    
    def getByUser(self, id_utilisateur):
        """Récupère les fichiers ajoutés par un utilisateur"""
        pass
    
    def update(self, id_fichier, nom, taille):
        """Met à jour les informations d'un fichier"""
        pass
    
    def delete(self, id_fichier):
        """Supprime un fichier audio"""
        pass
    
    def deleteByDay(self, jour_semaine):
        """Supprime tous les fichiers d'un jour"""
        pass
    
    def addToUser(self, id_fichier, id_utilisateur):
        """Associe un fichier à un utilisateur dans la table Ajoute"""
        pass
    
    def getTotalDuration(self, jour_semaine):
        """Calcule la durée totale des MP3 d'un jour"""
        pass
    
    def getTotalSize(self, jour_semaine):
        """Calcule la taille totale des MP3 d'un jour"""
        pass
    
    def getCount(self, jour_semaine):
        """Compte le nombre de fichiers d'un jour"""
        pass
    
    def getDownloadUrl(self, id_fichier):
        """Génère l'URL de téléchargement pour l'API"""
        pass
    
    def search(self, keyword):
        """Recherche des fichiers par nom ou artiste"""
        pass