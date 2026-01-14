from app import app


class log():
        
        def __init__(self,dico):
                self.id_log = dico['id_log']
                self.type_evenment = dico["type_evenement"]
                self.message = dico["message"]
                self.DateDeLog = dico["DateDeLog"] 
                self.niveau = dico["niveau"]     
                self.id_lecteur = dico["id_lecteur"]          