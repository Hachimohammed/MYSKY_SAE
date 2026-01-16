class User:
    
    def __init__(self, dico):
        self.id = dico["id_utilisateur"]
        self.nom=dico["nom"]
        self.prenom=dico["prenom"]
        self.email=dico["email"]
        self.id_Groupe=dico["id_Groupe"]
        self.nom_groupe=dico["nom_groupe"]