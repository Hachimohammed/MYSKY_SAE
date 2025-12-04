class User:

    def __init__(self, dico):
        self.id = dico["id"]
        self.username = dico["username"]
        self.role = dico["role"]