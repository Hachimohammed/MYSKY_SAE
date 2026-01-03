class PlanningDAOInterface:
    """Interface DAO pour les plannings hebdomadaires"""
    
    def create(self, nom_planning, date_debut, date_fin):
        """Crée un nouveau planning"""
        pass
    
    def getById(self, id_planning):
        """Récupère un planning par son ID"""
        pass
    
    def getAll(self):
        """Récupère tous les plannings"""
        pass
    
    def getActive(self):
        """Récupère uniquement les plannings actifs"""
        pass
    
    def getCurrent(self):
        """Récupère le planning actif en cours (selon la date)"""
        pass
    
    def update(self, id_planning, nom_planning, date_debut, date_fin):
        """Met à jour un planning"""
        pass
    
    def delete(self, id_planning):
        """Supprime un planning"""
        pass
    
    def setActive(self, id_planning, actif):
        """Active ou désactive un planning"""
        pass
    
    def getPlaylists(self, id_planning):
        """Récupère toutes les playlists d'un planning"""
        pass
    
    def generateFullWeek(self, id_planning):
        """Génère toutes les playlists pour une semaine complète"""
        pass
    
    def duplicatePlanning(self, id_planning, nouvelle_date_debut, nouvelle_date_fin):
        """Duplique un planning existant avec de nouvelles dates"""
        pass