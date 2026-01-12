from app import app

class Playlist:
    """Modèle représentant une playlist M3U"""
    
    def __init__(self, dico):
        self.id_playlist = dico.get('id_playlist')
        self.nom_playlist = dico.get('nom_playlist')
        self.chemin_fichier_m3u = dico.get('chemin_fichier_m3u')
        self.duree_total = dico.get('duree_total')
        self.id_planning = dico.get('id_planning')
        self.jour_semaine = dico.get('jour_semaine')
        self.date_creation = dico.get('date_creation')
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id_playlist': self.id_playlist,
            'nom_playlist': self.nom_playlist,
            'chemin_fichier_m3u': self.chemin_fichier_m3u,
            'duree_total': self.duree_total,
            'id_planning': self.id_planning,
            'jour_semaine': self.jour_semaine,
            'date_creation': self.date_creation
        }