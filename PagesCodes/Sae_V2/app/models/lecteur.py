from app import app

class lecteur():

    def __init__(self,dico):
        self.id_playlist = dico['id_id_lecteur']
        self.id_localisation = dico['id_localisation']
        self.nom_lecteur = dico['nom_lecteur']
        self.adresse_ip = dico['adresse_ip']
        self.emplacement = dico['emplacement']
        self.statut = dico['statut']