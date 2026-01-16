import sqlite3
import bcrypt
from app import app

class DatabaseInit:
    def __init__(self):
        self.database = app.root_path + '/musicapp.db'
        self._initDatabase()
    
    def _getDbConnection(self):
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON;") 
        conn.row_factory = sqlite3.Row
        return conn
    
    def _generatePwdHash(self, pwd):
        mdpHash = pwd.encode('utf-8')
        hashed = bcrypt.hashpw(mdpHash, bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    def _initDatabase(self):
        conn = self._getDbConnection()
        
        try:
            # 1. Table Groupe_Role
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Groupe_Role (
                    id_Groupe INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_groupe TEXT NOT NULL UNIQUE,
                    Description TEXT
                )
            """)

           
            # Initialisation de table Role avec 3 lignes seulement, 1 Admin, 2 Marketing, 3 Commercial
            conn.execute("""
                INSERT OR IGNORE INTO Groupe_Role(nom_groupe, Description)
                        VALUES
                            ('ADMIN', 'Administrateur Système'),
                            ('MARKETING', 'Service marketing alimentant la playlist'),
                            ('COMMERCIAL', 'Service commercial ajoutant des pubs à la playlist')
                """)
            
            # 2. Table Utilisateur 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Utilisateur (
                    id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    mdp TEXT NOT NULL,
                    id_Groupe INTEGER,
                    FOREIGN KEY (id_Groupe) REFERENCES Groupe_Role(id_Groupe)
                )
            """)
            
            # 3. Table Type_contenu
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Type_contenu (
                    id_Type_contenu INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_type TEXT NOT NULL UNIQUE,
                    description TEXT
                )
            """)

            # 4. Table localisation
            conn.execute("""
                CREATE TABLE IF NOT EXISTS localisation (
                    id_localisation INTEGER PRIMARY KEY AUTOINCREMENT,
                    ville TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL
                )
            """)

            # 5. Table planning
            conn.execute("""
                CREATE TABLE IF NOT EXISTS planning (
                    id_planning INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_planning TEXT NOT NULL,
                    date_debut TEXT NOT NULL,
                    date_fin TEXT NOT NULL,
                    actif_ou_non INTEGER DEFAULT 1
                )
            """)
            
            # 6. Table playlist 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS playlist (
                    id_playlist INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_playlist TEXT NOT NULL,
                    chemin_fichier_m3u TEXT NOT NULL,
                    duree_total INTEGER,
                    id_planning INTEGER,
                    jour_semaine TEXT,
                    date_heure_diffusion TEXT,
                    FOREIGN KEY (id_planning) REFERENCES planning(id_planning)
                )
            """)

            # 7. Table Fichier_audio 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Fichier_audio (
                    id_Fichier_audio INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    type_fichier TEXT NOT NULL,
                    taille INTEGER,
                    date_ajout TEXT NOT NULL,
                    id_Type_contenu INTEGER,
                    chemin_fichier TEXT,
                    duree INTEGER,
                    artiste TEXT,
                    album TEXT,
                    jour_semaine TEXT,
                    FOREIGN KEY (id_Type_contenu) REFERENCES Type_contenu(id_Type_contenu)
                )
            """)

            # 8. Table lecteur 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lecteur (
                    id_lecteur INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_lecteur TEXT NOT NULL,
                    adresse_ip TEXT UNIQUE NOT NULL,
                    statut TEXT DEFAULT 'DOWN',
                    id_localisation INTEGER,
                    FOREIGN KEY (id_localisation) REFERENCES localisation(id_localisation)
                )
            """)
            
            # 9. Table Log 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Log (
                    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_evenement TEXT NOT NULL,
                    message TEXT NOT NULL,
                    DateDeLog TEXT NOT NULL,
                    Niveau TEXT NOT NULL,
                    id_lecteur INTEGER,
                    FOREIGN KEY (id_lecteur) REFERENCES lecteur(id_lecteur)
                )
            """)
            
            # Relation Ajoute 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Ajoute (
                    id_utilisateur INTEGER NOT NULL,
                    id_Fichier_audio INTEGER NOT NULL,
                    Date_Ajout TEXT NOT NULL,
                    PRIMARY KEY (id_utilisateur, id_Fichier_audio),
                    FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur),
                    FOREIGN KEY (id_Fichier_audio) REFERENCES Fichier_audio(id_Fichier_audio)
                )
            """)
            
            # Relation fait_partie_de 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fait_partie_de (
                    id_Fichier_audio INTEGER NOT NULL,
                    id_playlist INTEGER NOT NULL,
                    ordre INTEGER DEFAULT 0,
                    PRIMARY KEY (id_Fichier_audio, id_playlist),
                    FOREIGN KEY (id_Fichier_audio) REFERENCES Fichier_audio(id_Fichier_audio),
                    FOREIGN KEY (id_playlist) REFERENCES playlist(id_playlist)
                )
            """)
            
            # Relation joue_dans
            conn.execute("""
                CREATE TABLE IF NOT EXISTS joue_dans (
                    id_playlist INTEGER NOT NULL,
                    id_lecteur INTEGER NOT NULL,
                    date_diffusion TEXT NOT NULL,
                    PRIMARY KEY (id_playlist, id_lecteur),
                    FOREIGN KEY (id_playlist) REFERENCES playlist(id_playlist),
                    FOREIGN KEY (id_lecteur) REFERENCES lecteur(id_lecteur)
                )
            """)

            # --- Insertions par défaut ---
            self._createDefaultTypes(conn)
            self._createDefaultAdmin(conn)
            
            conn.commit()
            print("Base de données initialisée avec succès !")
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation : {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _createDefaultAdmin(self, conn):
       # """Crée les groupes par défaut et l'utilisateur LeadAdmin"""
        try:
           
          #  groupes_defaut = [
           #     ('ADMIN', 'Administrateur Système'),
             #   ('COMMERCIAL', 'Équipe Commerciale'),
              #  ('MARKETING', 'Équipe Marketing')
            #]
            
            #for nom_groupe, description in groupes_defaut:
             #   conn.execute(
              #      'INSERT OR IGNORE INTO Groupe_Role (nom_groupe, Description) VALUES (?, ?)', 
               #     (nom_groupe, description)
                #)
            
          
            res = conn.execute('SELECT id_Groupe FROM Groupe_Role WHERE nom_groupe = ?', ('ADMIN',)).fetchone()
            admin_group_id = res['id_Groupe']

            existing = conn.execute('SELECT * FROM Utilisateur WHERE email = ?', 
                                    ('leadadmin@mysky.com',)).fetchone()
            
            if existing is None:
                mdp_hash = self._generatePwdHash('mysky123')
                conn.execute("""
                    INSERT INTO Utilisateur (nom, prenom, email, mdp, id_Groupe) 
                    VALUES (?, ?, ?, ?, ?)
                """, ('Admin', 'Lead', 'leadadmin@mysky.com', mdp_hash, admin_group_id))
                
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de l'admin : {e}")

    def _createDefaultTypes(self, conn):
        """Ajoute les types de contenu par défaut"""
        try:
            types_defaut = [
                ('MUSIQUE', 'Fichier audio musical'),
                ('PUB', 'Publicité audio'),
                ('ANNONCE', 'Annonce ou message'),
                ('AUTRE', 'Autre type de fichier audio')
            ]
            
            for nom_type, description in types_defaut:
                conn.execute("""
                    INSERT OR IGNORE INTO Type_contenu (nom_type, description)
                    VALUES (?, ?)
                """, (nom_type, description))
        except sqlite3.Error as e:
            print(f"Erreur lors de l’insertion des types par défaut : {e}")


