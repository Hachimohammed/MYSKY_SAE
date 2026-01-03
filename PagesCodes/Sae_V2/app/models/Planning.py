from app import app

class Planning:
    """Modèle représentant un planning hebdomadaire"""
    
    def __init__(self, dico):
        self.id_planning = dico.get('id_planning')
        self.nom_planning = dico.get('nom_planning')
        self.date_debut = dico.get('date_debut')
        self.date_fin = dico.get('date_fin')
        self.actif = dico.get('actif_ou_non', 1)
        self.date_creation = dico.get('date_creation')
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id_planning': self.id_planning,
            'nom_planning': self.nom_planning,
            'date_debut': self.date_debut,
            'date_fin': self.date_fin,
            'actif': self.actif,
            'date_creation': self.date_creation
        }