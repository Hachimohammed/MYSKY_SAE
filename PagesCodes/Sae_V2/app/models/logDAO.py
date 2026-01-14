from app import app
from app.models.log import log
import sqlite3


class logDAO():

    def __init__(self):
        self.database = app.root_path + '/musicapp.db'

    
    def _getDBConnection(self):
        """Obtient une connexion à la base de données"""
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn
    
    def addEvent(self,type_evenement,message,DateDelog,niveau,id_lecteur):
        conn = self._getDBConnection()
        conn.execute("INSERT OR IGNORE INTO log (type_evenement,message,DateDeLog,niveau,id_lecteur)" 
        "VALUES (?,?,?,?,?)",(type_evenement,message,DateDelog,niveau,id_lecteur))
