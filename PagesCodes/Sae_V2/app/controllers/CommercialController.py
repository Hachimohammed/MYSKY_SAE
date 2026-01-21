from flask import render_template, redirect, url_for, jsonify, send_file, request 
from app import app
import os
from mutagen.mp3 import MP3 as mp3
from app.services.AudioFileService import AudioFileService
from app.services.PlaylistService import PlaylistService
from app.services.AdminService import AdminService
from app.controllers.LoginController import reqrole
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'audio')
ALLOWED_EXTENSIONS = {'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

audio_service = AudioFileService()
playlist_service = PlaylistService()
admin_service = AdminService()

class CommercialController:

    #Classe dédiée au contrôle des accès liés aux commerciaux

    @app.route('/commercial')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialView():
        metadata = {"title": "Commercial Dashboard"}
        return render_template('commercial.html', metadata=metadata)
    
    
    @app.route('/commercial/upload', methods=['POST'])
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialUpload():
        try:
            # admin_service.Ad(recuperation des mp3 mais si c'est pas-possible-je-modifie)
            if 'filename' not in request.files:
                return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400

            file = request.files['filename']

            if file.filename == '':
                return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)


                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                
                audio = mp3(filepath)
                duration = audio.info.length

                
                audio_service.createAudioFile(filename, filepath, duration)

                return jsonify({
                    'success': True, 
                    'filename': filename,
                    'duration': duration
                }), 200
            else:
                return jsonify({'success': False, 'error': 'Format de fichier non autorisé'}), 400

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/commercial/file/<int:file_id>', methods=['DELETE'])
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialDeleteFile(id_fichier):
        try:
            success, error = audio_service.deleteAudioFile(id_fichier)

            if success:
                return jsonify({'success': True}), 200
            else:
                return jsonify({'success': False, 'error': error}), 404 if error == 'Fichier introuvable' else 500
            
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier : {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/commercial/files/generate', methods=['POST'])
    @reqrole("ADMIN", "COMMERCIAL")
    def generateFileLecture():
            file_upload = audio_service.createAudioFile()
            if file_upload == True:
                try:
                    admin_service.pullMP3toplayers()
                    print("Fichiers MP3 envoyés aux players.")

                except Exception as e:
                    print(f"Erreur lors de l'envoi des fichiers MP3 aux players : {e}")
                    return jsonify({"error": str(e)}), 500
            return redirect(url_for('commercialView'))


    @app.route('/commercial/playlist/stop')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialStopPlaylist():
        try:
            admin_service.WhatPlayerPlaying()
            if admin_service.WhatPlayerPlaying() == True:
                admin_service.getAllDown()
                print("Lecture en cours arrêtée sur tous les players.")
                

                
        except Exception as e:
            print(f"Aucune playlist en cours d'exécution. : {e}")
            return jsonify({"error": str(e)}), 500
        
        return redirect(url_for('commercialView'))
    

    @app.route('/api/v1/files/download/<int:id_fichier>')
    @reqrole("ADMIN", "COMMERCIAL")
    def api_download_audio_file(id_fichier):
        try:
            audio_ficher = audio_service.getAudioFileById(id_fichier)

            if not audio_ficher:
                return jsonify({"error": "Fichier non trouvé"}), 404
            
            if not audio_ficher.chemin_fichier or not os.path.exists(audio_ficher.chemin_fichier):
                return jsonify({"error": "Chemin du fichier invalide"}), 404
            
            return send_file(
                audio_ficher.chemin_fichier,
                mimetype='audio/mp3',
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