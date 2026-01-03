from app import app

class AudioFile:
    """Modèle représentant un fichier audio MP3"""
    
    def __init__(self, dico):
        self.id_fichier = dico.get('id_Fichier_audio')
        self.nom = dico.get('nom')
        self.type_fichier = dico.get('type_fichier', 'mp3')
        self.taille = dico.get('taille')
        self.date_ajout = dico.get('date_ajout')
        self.id_type_contenu = dico.get('id_Type_contenu', 1)
        self.chemin_fichier = dico.get('chemin_fichier')
        self.duree = dico.get('duree')
        self.artiste = dico.get('artiste')
        self.album = dico.get('album')
        self.jour_semaine = dico.get('jour_semaine')
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id_fichier': self.id_fichier,
            'nom': self.nom,
            'type_fichier': self.type_fichier,
            'taille': self.taille,
            'date_ajout': self.date_ajout,
            'id_type_contenu': self.id_type_contenu,
            'chemin_fichier': self.chemin_fichier,
            'duree': self.duree,
            'artiste': self.artiste,
            'album': self.album,
            'jour_semaine': self.jour_semaine
        }