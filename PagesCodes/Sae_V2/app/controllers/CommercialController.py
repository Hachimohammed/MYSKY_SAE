from flask import render_template, jsonify, request, session, url_for
from app import app
import os
from mutagen.mp3 import MP3
from datetime import datetime
from app.services.AudioFileService import AudioFileService
from app.controllers.LoginController import reqrole
from werkzeug.utils import secure_filename
from app.models.lecteurDAO import lecteurDAO

# Configuration
UPLOAD_FOLDER_PUB = os.path.join(app.root_path, 'static', 'commercial')
ALLOWED_EXTENSIONS = {'mp3'}

os.makedirs(UPLOAD_FOLDER_PUB, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

audio_service = AudioFileService(app)
lecteur_dao = lecteurDAO()


class CommercialController:

    @app.route('/commercial')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercialView():
        """Page principale commerciale"""
        # Récupérer les infos du lecteur
        playing_info = None
        try:
            playing_info = lecteur_dao.WhatPlayerPlaying()
            if playing_info:
                print(f" Lecture en cours: {playing_info.get('name')} à {playing_info.get('localisation')}")
            else:
                print(" Aucun lecteur actif ou aucune lecture en cours")
        except Exception as e:
            print(f" Erreur récupération info lecteur: {e}")
            playing_info = None
        
        
        ads_history = []
        try:
            all_files = audio_service.getAllAudioFiles()
            ads = [f for f in all_files if f.id_type_contenu == 2]
            ads.sort(key=lambda x: x.date_ajout, reverse=True)
            
            
            for ad in ads[:10]:
                try:
                    date_ajout = datetime.fromisoformat(ad.date_ajout)
                    now = datetime.now()
                    diff = now - date_ajout
                    
                    if diff.days > 0:
                        time_ago = f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
                    elif diff.seconds >= 3600:
                        hours = diff.seconds // 3600
                        time_ago = f"il y a {hours} heure{'s' if hours > 1 else ''}"
                    elif diff.seconds >= 60:
                        minutes = diff.seconds // 60
                        time_ago = f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
                    else:
                        time_ago = "à l'instant"
                except:
                    time_ago = "Date inconnue"
                
                if ad.duree:
                    minutes = ad.duree // 60
                    seconds = ad.duree % 60
                    duree_format = f"{minutes}:{seconds:02d}"
                else:
                    duree_format = "0:00"
                
                ads_history.append({
                    'id': ad.id_fichier,
                    'nom': ad.nom + '.mp3',
                    'duree': duree_format,
                    'time_ago': time_ago,
                    'statut': ad.statut_diffusion
                })
        except Exception as e:
            print(f"❌ Erreur récupération historique: {e}")
        
        return render_template('commercial.html', 
                             playing_info=playing_info,
                             ads_history=ads_history)


    @app.route('/commercial/upload-ad', methods=['POST'])
    @reqrole("ADMIN", "COMMERCIAL")
    def commercial_upload_ad():
        """Upload de publicité"""
        try:
            if 'filename' not in request.files:
                return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400

            file = request.files['filename']

            if file.filename == '':
                return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400

            if not allowed_file(file.filename):
                return jsonify({'success': False, 'error': 'Seuls les fichiers MP3 sont autorisés'}), 400

            # Sauvegarde du fichier
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER_PUB, filename)
            file.save(filepath)
            print(f"Publicité sauvegardée : {filepath}")

            # Extraction de la durée
            try:
                audio = MP3(filepath)
                duration = int(audio.info.length)
            except Exception as e:
                print(f" Erreur lecture métadonnées : {e}")
                duration = 45

            # Enregistrement en BDD avec statut EN_ATTENTE
            user_id = session.get('user_id', 1)
            audio_file = audio_service.createAudioFile(
                nom=filename.rsplit('.', 1)[0],
                type_fichier='mp3',
                taille=os.path.getsize(filepath),
                chemin_fichier=filepath,
                id_type_contenu=2,  # Type PUB
                duree=duration,
                jour_semaine=None,
                id_utilisateur=user_id
            )

            if not audio_file:
                return jsonify({
                    'success': False,
                    'error': 'Erreur lors de l\'enregistrement en base de données'
                }), 500

            return jsonify({
                'success': True,
                'filename': filename,
                'duration': duration,
                'id_fichier': audio_file.id_fichier,
                'statut': audio_file.statut_diffusion
            }), 200

        except Exception as e:
            print(f"❌ Erreur upload ad : {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500


    # ========== API POUR LES LECTEURS ==========

    @app.route('/api/v1/commercial/ads-for-players', methods=['GET'])
    def api_get_ads_for_players():
        """
        API pour les lecteurs : récupère uniquement les publicités EN_ATTENTE
        
        Les lecteurs appellent cette API toutes les 2 secondes pour vérifier 
        s'il y a de nouvelles pubs à diffuser
        
        ACCÈS: Public (pas d'authentification requise)
        
        """
        try:
            all_files = audio_service.getAllAudioFiles()
            
            ads = [f for f in all_files if f.id_type_contenu == 2 and f.statut_diffusion == 'EN_ATTENTE']
            
        
            ads.sort(key=lambda x: x.date_ajout, reverse=True)
            
            ads_data = []
            for ad in ads:
                ads_data.append({
                    'id_fichier': ad.id_fichier,
                    'nom': ad.nom,
                    'duree': ad.duree,
                    'date_ajout': ad.date_ajout,
                    'statut': ad.statut_diffusion,
                    'download_url': url_for('api_download_audio', id_fichier=ad.id_fichier, _external=True)
                })
            
            return jsonify({
                'success': True,
                'count': len(ads_data),
                'ads': ads_data
            }), 200
            
        except Exception as e:
            print(f"Erreur get ads for players: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/v1/commercial/mark-ad-as-played/<int:id_fichier>', methods=['POST'])
    def api_mark_ad_as_played(id_fichier):
        """
        API pour les lecteurs : marque une pub comme TERMINE après diffusion
        
        ACCÈS: Public (pas d'authentification requise)
        """
        try:
            success = audio_service.audio_dao.updateStatutDiffusion(id_fichier, 'TERMINE')
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Publicité {id_fichier} marquée comme terminée'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Erreur lors de la mise à jour'
                }), 500
                
        except Exception as e:
            print(f"Erreur mark ad as played: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/v1/player/current', methods=['GET'])
    def api_get_current_player():
        """
        API pour récupérer ce qui est en train de jouer sur les lecteurs
        
        ACCÈS: Public (pas d'authentification requise)
        """
        try:
            playing_info = lecteur_dao.WhatPlayerPlaying()
            
            if playing_info:
                return jsonify({
                    'success': True,
                    'playing': playing_info
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'playing': None
                }), 200
                
        except Exception as e:
            print(f"Erreur get current player: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500