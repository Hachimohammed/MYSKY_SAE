from app import app
from app.models.log import log
import datetime
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
        conn.commit()
        conn.close
    
            
    
    def WriteLog(self,date_debut,date_fin):
        conn = self._getDBConnection()
        logs = conn.execute("SELECT * FROM Log WHERE (?) > DateDeLog AND DateDeLog < (?) ",(date_debut,date_fin)).fetchall()
        with open(f"~/MYSKY_SAE/PagesCodes/Sae_V2/app/static/log_{datetime.now()}", 'w') as file:
            for log in logs:
                file.write(log)
        conn.close()  