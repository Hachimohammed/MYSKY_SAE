from app import app

class lecteur():

    def __init__(self,dico):
        self.id_lecteur = dico['id_lecteur']
        self.id_localisation = dico['id_localisation']
        self.nom_lecteur = dico['nom_lecteur']
        self.adresse_ip = dico['adresse_ip']
        self.statut = dico['statut']