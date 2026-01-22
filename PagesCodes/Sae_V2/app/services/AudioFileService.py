from app.models.AudioFileDAO import AudioFileDAO
from werkzeug.utils import secure_filename
from mutagen.mp3 import MP3
import os
import json
from datetime import datetime
from flask import url_for

class AudioFileService:
    """Service contenant TOUTE la logique métier des fichiers audio"""
    
    def __init__(self, app=None):
        self.audio_dao = AudioFileDAO()
        self.app = app
    
    # ==================== MÉTHODES DE BASE ====================
    
    def getAllAudioFiles(self):
        """Récupère tous les fichiers audio"""
        return self.audio_dao.getAll()
    
    def getAudioFileById(self, id_fichier):
        """Récupère un fichier audio par son ID"""
        return self.audio_dao.getById(id_fichier)
    
    def getAudioFilesByDay(self, jour_semaine):
        """Récupère tous les fichiers audio d'un jour spécifique"""
        return self.audio_dao.getByDay(jour_semaine)
    
    def createAudioFile(self, nom, type_fichier, taille, chemin_fichier, 
                       id_type_contenu=1, duree=None, artiste=None, 
                       album=None, jour_semaine=None, id_utilisateur=None):
        """Crée un nouveau fichier audio"""
        return self.audio_dao.create(nom, type_fichier, taille, chemin_fichier, 
                                     id_type_contenu, duree, artiste, album, 
                                     jour_semaine, id_utilisateur)
    
    def updateAudioFile(self, id_fichier, nom, taille):
        """Met à jour un fichier audio"""
        return self.audio_dao.update(id_fichier, nom, taille)
    
    def deleteAudioFile(self, id_fichier):
        """Supprime un fichier audio"""
        return self.audio_dao.delete(id_fichier)
    
    def deleteAudioFilesByDay(self, jour_semaine):
        """Supprime tous les fichiers d'un jour"""
        return self.audio_dao.deleteByDay(jour_semaine)
    
    def searchAudioFiles(self, keyword):
        """Recherche des fichiers par mot-clé"""
        return self.audio_dao.search(keyword)
    
    def getAudioFilesByUser(self, id_utilisateur):
        """Récupère les fichiers ajoutés par un utilisateur"""
        return self.audio_dao.getByUser(id_utilisateur)
    
    def getAudioFilesByType(self, id_type_contenu):
        """Récupère les fichiers par type de contenu"""
        return self.audio_dao.getByType(id_type_contenu)
    
    def getDownloadUrl(self, id_fichier):
        """Génère l'URL de téléchargement"""
        return self.audio_dao.getDownloadUrl(id_fichier)
    
    def addAudioFileToUser(self, id_fichier, id_utilisateur):
        """Associe un fichier à un utilisateur"""
        return self.audio_dao.addToUser(id_fichier, id_utilisateur)
    
    # ==================== LOGIQUE MÉTIER AVANCÉE ====================
    
    def getDayStatistics(self, jour_semaine):
        """Récupère les statistiques d'un jour"""
        fichiers = self.getAudioFilesByDay(jour_semaine)
        
        total_duration = sum(f.duree for f in fichiers if f.duree)
        total_size = sum(f.taille for f in fichiers if f.taille)
        count = len(fichiers)
        
        return {
            "jour": jour_semaine,
            "count": count,
            "duree_totale": total_duration,
            "taille_totale": total_size
        }
    
    def getWeekStatistics(self):
        """Récupère les statistiques de toute la semaine"""
        jours = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
        
        stats_par_jour = {}
        total_musiques = 0
        total_duree = 0
        total_taille = 0

        for jour in jours:
            stats = self.getDayStatistics(jour)
            stats_par_jour[jour] = stats
            
            total_musiques += stats['count']
            total_duree += stats['duree_totale']
            total_taille += stats['taille_totale']

        return {
            'par_jour': stats_par_jour,
            'totaux': {
                'nombre_musiques': total_musiques,
                'duree_totale': total_duree,
                'taille_totale': total_taille
            }
        }
    
    # ==================== GESTION DES FICHIERS PHYSIQUES ====================
    
    def extractMp3Metadata(self, filepath):
        """Extrait les métadonnées d'un fichier MP3"""
        try:
            audio = MP3(filepath)
            return {
                'duree': int(audio.info.length),
                'artiste': str(audio.get('TPE1', ['Inconnu'])[0]) if 'TPE1' in audio else 'Inconnu',
                'album': str(audio.get('TALB', ['Inconnu'])[0]) if 'TALB' in audio else 'Inconnu',
                'titre': str(audio.get('TIT2', [''])[0]) if 'TIT2' in audio else None
            }
        except Exception as e:
            print(f"Erreur metadata MP3: {e}")
            return {
                'duree': 0,
                'artiste': 'Inconnu',
                'album': 'Inconnu',
                'titre': None
            }
    
    def uploadMultipleFiles(self, files, jour_semaine, app_root_path, id_utilisateur=1):
        """Upload plusieurs fichiers MP3 pour un jour donné"""
        uploaded_count = 0
        errors = []

        for file in files:
            if file.filename == '':
                continue
            
            filename = secure_filename(file.filename)
            folder_full = os.path.join(app_root_path, 'static', 'audio', jour_semaine)
            os.makedirs(folder_full, exist_ok=True)
            
            path_full = os.path.join(folder_full, filename)
            file.save(path_full)
            
            meta = self.extractMp3Metadata(path_full)

            audio = self.createAudioFile(
                nom=meta['titre'] or filename.rsplit('.', 1)[0],
                type_fichier='mp3',
                taille=os.path.getsize(path_full),
                chemin_fichier=path_full,
                id_type_contenu=1,
                duree=meta['duree'],
                artiste=meta['artiste'],
                album=meta['album'],
                jour_semaine=jour_semaine,
                id_utilisateur=id_utilisateur
            )

            if audio:
                uploaded_count += 1
            else:
                errors.append(f"Erreur BDD pour {filename}")
                if os.path.exists(path_full): 
                    os.remove(path_full)

        return uploaded_count, errors
    
    def deleteAudioFileWithPhysicalFile(self, id_fichier):
        """Supprime un fichier audio de la BDD ET du disque"""
        audio = self.getAudioFileById(id_fichier)
        
        if not audio:
            return False, 'Fichier introuvable'

        if audio.chemin_fichier and os.path.exists(audio.chemin_fichier):
            try:
                os.remove(audio.chemin_fichier)
                print(f" Fichier supprimé: {audio.chemin_fichier}")
            except Exception as e:
                print(f"Erreur suppression fichier: {e}")

        if self.deleteAudioFile(id_fichier):
            return True, None
        else:
            return False, 'Erreur suppression BDD'
    
    def deleteDayFilesWithPhysical(self, jour_semaine):
        """Supprime tous les fichiers d'un jour (BDD + disque)"""
        fichiers = self.getAudioFilesByDay(jour_semaine)
        deleted_count = 0

        for f in fichiers:
            if f.chemin_fichier and os.path.exists(f.chemin_fichier):
                try:
                    os.remove(f.chemin_fichier)
                    print(f"Fichier supprimé: {f.chemin_fichier}")
                except Exception as e:
                    print(f"Erreur suppression fichier {f.chemin_fichier}: {e}")
            
            if self.deleteAudioFile(f.id_fichier):
                deleted_count += 1

        return deleted_count
    
    # ==================== GESTION DE L'ORDRE ====================
    
    def savePlaybackOrder(self, jour_semaine, fichiers_ordre, ordre_folder, date_diffusion=None, heure_diffusion=None):
        """Sauvegarde l'ordre de lecture des fichiers pour un jour"""
        os.makedirs(ordre_folder, exist_ok=True)
        
        ordre_file = os.path.join(ordre_folder, f"ordre_{jour_semaine}.json")
        data = {
            'jour': jour_semaine,
            'fichiers_ordre': fichiers_ordre,
            'date_sauvegarde': datetime.now().isoformat()
        }
        if date_diffusion and heure_diffusion:
            data['date_heure_diffusion'] = f"{date_diffusion} {heure_diffusion}"
        
        with open(ordre_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f" Ordre sauvegardé dans {ordre_file}")
        return True
    
    def loadPlaybackOrder(self, jour_semaine, ordre_folder):
        """Charge l'ordre de lecture sauvegardé pour un jour"""
        ordre_file = os.path.join(ordre_folder, f"ordre_{jour_semaine}.json")
        fichiers_ordonnes = []
        
        if os.path.exists(ordre_file):
            with open(ordre_file, 'r', encoding='utf-8') as f:
                ordre_data = json.load(f)
                fichiers_ids = ordre_data.get('fichiers_ordre', [])
                
                for id_fichier in fichiers_ids:
                    audio = self.getAudioFileById(id_fichier)
                    if audio:
                        fichiers_ordonnes.append(audio)
                
                print(f" Ordre chargé pour {jour_semaine}: {len(fichiers_ordonnes)} fichiers")
        else:
            fichiers_ordonnes = self.getAudioFilesByDay(jour_semaine)
            print(f" Pas d'ordre pour {jour_semaine}, utilisation ordre par défaut")
        
        return fichiers_ordonnes
    
    def getDateHeureDiffusion(self, jour_semaine, ordre_folder):
        """Récupère la date/heure de diffusion sauvegardée pour un jour"""
        ordre_file = os.path.join(ordre_folder, f"ordre_{jour_semaine}.json")
    
        if not os.path.exists(ordre_file):
            return None
        
        try:
            with open(ordre_file, 'r', encoding='utf-8') as f:
                ordre_data = json.load(f)
                return ordre_data.get('date_heure_diffusion')
        except Exception as e:
            print(f"❌ Erreur getDateHeureDiffusion: {e}")
            return None
    
    # ==================== FORMATAGE POUR API ====================
    
    def formatAudioFileForApi(self, audio_file, include_download_url=True):
        """Formate un fichier audio pour l'API avec URL de téléchargement"""
        data = audio_file.to_dict()
        
        if include_download_url:
            data['download_url'] = url_for(
                'api_download_audio',
                id_fichier=audio_file.id_fichier,
                _external=True
            )
        
        return data
    
    def formatAudioFilesForApi(self, audio_files, include_download_url=True):
        """Formate une liste de fichiers audio pour l'API"""
        return [self.formatAudioFileForApi(f, include_download_url) for f in audio_files]
    
    def getAudioFilesForOrdering(self, jour_semaine):
        """Récupère les fichiers formatés pour l'interface d'ordonnancement"""
        fichiers = self.getAudioFilesByDay(jour_semaine)
        
        fichiers_data = []
        for f in fichiers:
            fichiers_data.append({
                'id': f.id_fichier,
                'nom': f.nom,
                'artiste': f.artiste or 'Inconnu',
                'duree': f.duree or 0,
                'duree_formattee': f"{f.duree // 60}:{f.duree % 60:02d}" if f.duree else "0:00"
            })
        
        return fichiers_data
    
 