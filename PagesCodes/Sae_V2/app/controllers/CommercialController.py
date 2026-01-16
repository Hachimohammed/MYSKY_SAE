from flask import render_template, redirect, url_for, request 
from app import app
import os
from mutagen.mp3 import MP3 as mp3
from app.services.AudioFileService import AudioFileService
from app.services.PlaylistService import PlaylistService
from app.controllers.LoginController import reqrole
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'audio')
ALLOWED_EXTENSIONS = {'mp3'}

def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        metadata = {"title": "Upload Audio File"}
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
                AudioFileService.save_audio_file(filename, filepath, duration)
                
                return redirect(url_for('commercialView'))
            
            else:
                return "No file selected", 400
            
        return render_template('commercial.html', metadata=metadata)
    

    @app.route('/commercial/files')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialFiles():
        metadata = {"title": "Audio Files List"}
        audio_files = AudioFileService.get_all_audio_files()
        return render_template('commercial_files.html', metadata=metadata, audio_files=audio_files)
    
    
    @app.route('/commercial/play/<int:file_id>')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialPlayFile(file_id):
        metadata = {"title": "Play Audio File"}
        audio_file = AudioFileService.get_audio_file_by_id(file_id)
        return render_template('commercial_play.html', metadata=metadata, audio_file=audio_file)
    

    @app.route('/commercial/delete/<int:file_id>', methods=['POST'])
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialDeleteFile(file_id):
        AudioFileService.delete_audio_file(file_id)
        return redirect(url_for('commercialFiles'))
    
    
    @app.route('/commercial/playlist/stop')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialStopPlaylist():
        upload = upload.commercialUpload()
        if upload == True:
            if PlaylistService.is_playlist_running():
                PlaylistService.stop_playlist()
                print("Playlist arrêtée.")
            else:
                print("Aucune playlist en cours d'exécution.")
        return redirect(url_for('commercialView'))
