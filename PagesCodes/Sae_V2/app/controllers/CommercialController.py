from flask import render_template, redirect, url_for, jsonify, send_file, request 
from app import app
import os
from mutagen.mp3 import MP3 as mp3
from app.services.AudioFileService import AudioFileService
from app.services.PlaylistService import PlaylistService
from app.controllers.LoginController import reqrole
from app.controllers.AdminController import sync_selected_players
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'audio')
ALLOWED_EXTENSIONS = {'mp3'}

def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

audio_service = AudioFileService()
playlist_service = PlaylistService()

class CommercialController:

    #Classe dédiée au contrôle des accès liés aux commerciaux

    @app.route('/commercial')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialView():
        metadata = {"title": "Commercial Dashboard"}
        return render_template('commercial.html', metadata=metadata)
    
    
    @app.route('/commercial/upload', methods=['POST'])
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialUpload(upload):
        metadata = {"title": "Upload fichier Audio"}
        if request.method == 'POST':
            # Gérer le téléchargement du fichier audio
            file = request.files['audiofile']
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                # Extraire la durée du fichier audio
                audio = mp3(filepath)
                duration = audio.info.length  # Durée en secondes

                # Enregistrer les informations dans la base de données
                audio_service.createAudioFile(filename, filepath, duration)
                
                return redirect(url_for('commercialView'))
            
            else:
                return "Aucun ficher selectionner", 400
            
        return render_template('commercial.html', metadata=metadata)
    

    @app.route('/commercial/files')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialFiles():
        metadata = {"title": "Audio Files List"}
        audio_files = audio_service.getAllAudioFiles()
        return render_template('commercial_files.html', metadata=metadata, audio_files=audio_files)
    
    
    @app.route('/commercial/play/<int:file_id>')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialPlayFile(file_id):
        metadata = {"title": "Play Audio File"}
        audio_file = audio_service.getAudioFileById(id_fichier=file_id)
        return render_template('commercial_play.html', metadata=metadata, audio_file=audio_file)
    

    @app.route('/commercial/delete/<int:file_id>', methods=['DELETE'])
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialDeleteFile(file_id):
        audio_service.deleteAudioFile(id_fichier=file_id)
        return redirect(url_for('commercialFiles'))
    
    
    @app.route('/commercial/playlist/stop')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialStopPlaylist():
        upload = upload.commercialUpload()
        if upload == True:
            if playlist_service.is_playlist_running():
                playlist_service.stop_playlist()
                print("Playlist arrêtée.")
            else:
                print("Aucune playlist en cours d'exécution.")
        return redirect(url_for('commercialView'))
    

    @app.route('/api/v1/files/download/<int:file_id>')
    @reqrole("ADMIN", "COMMERCIAL")
    def api_download_audio_file(id_fichier):
        try:
            audio_ficher = audio_service.getAudioFileById(id_fichier)

            if not audio_ficher:
                return jsonify({"error": "Fichier non trouvé"}), 404
            
            return send_file(
                audio_ficher.chemin_fichier,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=f"{audio_ficher.nom}.mp3"
            )
       
        except Exception as e:
            print(f"Erreur lors du téléchargement du fichier : {e}")
            return jsonify({"error": str(e)}), 500        


    @app.route('/api/v1/files')
    @reqrole("ADMIN", "COMMERCIAL")
    def api_get_audio_files():
        try:
            audio_fichier = audio_service.getAllAudioFiles()

            fichier_data = []
            for f in audio_fichier:
                fichier_data.append({
                "id": f.id_fichier,
                "nom": f.nom,
                "type": f.type_fichier,
                "taille": f.taille,
                "date_ajout": f.date_ajout,
                "id_type": f.id_type_contenu,
                "chemin": f.chemin_fichier,
                "duree": f.duree,
                "artiste": f.artiste,
                "album": f.album,
                "jour_semaine": f.jour_semaine
            })
        
            return jsonify(fichier_data)
    
        except Exception as e:
            print(f"Erreur lors de la récupération des fichiers : {e}")
            return jsonify({"error": str(e)}), 500
    
        
    
    @app.route('/api/v1/players/sync', methods=['POST'])
    @reqrole("ADMIN", "COMMERCIAL")
    def api_sync_players():
        data = request.get_json()
        player_ids = data.get('player_ids', [])
        sync_selected_players(player_ids)
        return jsonify({"status": "success", "message": "Players synchronized successfully."})
        
    