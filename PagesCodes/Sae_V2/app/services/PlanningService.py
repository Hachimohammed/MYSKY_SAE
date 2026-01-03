from app.models.PlanningDAO import PlanningDAO
from datetime import datetime, timedelta

class PlanningService:
    """
    Classe dédiée à la logique métier des plannings
    """
    
    def __init__(self):
        self.planning_dao = PlanningDAO()
    
    def getAllPlannings(self):
        """Récupère tous les plannings"""
        return self.planning_dao.getAll()
    
    def getPlanningById(self, id_planning):
        """Récupère un planning par son ID"""
        return self.planning_dao.getById(id_planning)
    
    def getActivePlannings(self):
        """Récupère uniquement les plannings actifs"""
        return self.planning_dao.getActive()
    
    def getCurrentPlanning(self):
        """Récupère le planning actif en cours selon la date du jour"""
        return self.planning_dao.getCurrent()
    
    def createPlanning(self, nom_planning, date_debut, date_fin):
        """Crée un nouveau planning"""
        return self.planning_dao.create(nom_planning, date_debut, date_fin)
    
    def updatePlanning(self, id_planning, nom_planning, date_debut, date_fin):
        """Met à jour un planning existant"""
        return self.planning_dao.update(id_planning, nom_planning, date_debut, date_fin)
    
    def deletePlanning(self, id_planning):
        """Supprime un planning et ses playlists associées"""
        return self.planning_dao.delete(id_planning)
    
    def activatePlanning(self, id_planning):
        """Active un planning"""
        return self.planning_dao.setActive(id_planning, True)
    
    def deactivatePlanning(self, id_planning):
        """Désactive un planning"""
        return self.planning_dao.setActive(id_planning, False)
    
    def getPlanningPlaylists(self, id_planning):
        """Récupère toutes les playlists d'un planning"""
        return self.planning_dao.getPlaylists(id_planning)
    
    def generateWeeklyPlaylist(self, id_planning):
        """Génère toutes les playlists M3U pour une semaine complète"""
        return self.planning_dao.generateFullWeek(id_planning)
    
    def duplicatePlanning(self, id_planning, nouvelle_date_debut, nouvelle_date_fin):
        """Duplique un planning avec toutes ses playlists et fichiers audio"""
        return self.planning_dao.duplicatePlanning(id_planning, nouvelle_date_debut, nouvelle_date_fin)
    
    def createWeeklyPlanning(self, nom_planning, semaine_debut=None):
        """
        Crée un planning pour une semaine complète
        Calcule automatiquement la semaine si non fournie
        """
        if semaine_debut is None:
            today = datetime.now().date()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            date_debut = today + timedelta(days=days_until_monday)
        else:
            date_debut = semaine_debut
        
        date_fin = date_debut + timedelta(days=6)
        
        return self.planning_dao.create(
            nom_planning,
            date_debut.isoformat(),
            date_fin.isoformat()
        )
    
    def getPlanningStatistics(self, id_planning):
        """
        Récupère les statistiques complètes d'un planning
        Agrège plusieurs données du DAO
        """
        planning = self.getPlanningById(id_planning)
        if not planning:
            return None
        
        playlists = self.getPlanningPlaylists(id_planning)
        
        total_playlists = len(playlists)
        total_duration = sum(p.duree_total for p in playlists if p.duree_total)
        jours_couverts = list(set(p.jour_semaine for p in playlists if p.jour_semaine))
        
        return {
            "planning_id": id_planning,
            "nom": planning.nom_planning,
            "date_debut": planning.date_debut,
            "date_fin": planning.date_fin,
            "actif": planning.actif_ou_non,
            "nombre_playlists": total_playlists,
            "duree_totale": total_duration,
            "jours_couverts": jours_couverts,
            "jours_manquants": [
                jour for jour in ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE'] 
                if jour not in jours_couverts
            ]
        }
    
    def togglePlanningStatus(self, id_planning):
        """Inverse le statut actif/inactif d'un planning"""
        planning = self.getPlanningById(id_planning)
        if not planning:
            return False
        
        nouveau_statut = not planning.actif_ou_non
        return self.planning_dao.setActive(id_planning, nouveau_statut)