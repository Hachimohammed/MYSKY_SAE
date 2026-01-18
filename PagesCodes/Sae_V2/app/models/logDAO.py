from app import app
from app.models.log import log
from pathlib import Path
import sqlite3
import os


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
        
        date_range = f"{date_debut:%Y-%m-%d_%H-%M-%S}---{date_fin:%Y-%m-%d_%H-%M-%S}"
        # Expres pour qu'il puissent retrouver le projet n'importe ou 
        model_dir = Path(__file__).resolve().parent # "~app/model"
        static_dir = model_dir.parent / "static" # "~app/static" 
        static_dir.mkdir(parents=True, exist_ok=True)
        
        path  = static_dir / f"log_{date_range}.txt" # Open() comprend pas le '~' donc j'ai du utiliser le module os 
        with open(path, 'w') as file:
            file.write("========================================\n\n")
            file.write(date_range)
            file.write("\n\n========================================\n\n")
            for log in logs:
                file.write(log , "\n\n")
        conn.close()  