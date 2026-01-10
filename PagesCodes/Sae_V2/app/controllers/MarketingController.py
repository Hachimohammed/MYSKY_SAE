from flask import (
    render_template, request, jsonify, send_file,
    redirect, url_for, flash
)
import os
from datetime import datetime

from app import app
from app.services.AudioFileService import AudioFileService
from app.services.PlaylistService import PlaylistService
from app.services.PlanningService import PlanningService

# ==================== CONFIG ====================

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'audio')
ALLOWED_EXTENSIONS = {'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

audio_service = AudioFileService(app)
playlist_service = PlaylistService()
planning_service = PlanningService()

# ==================== UTILS ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== PAGE PRINCIPALE ====================

@app.route('/marketing')
@app.route('/marketing/dashboard')
def marketing_dashboard():
    try:
        jours = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
        stats_jours = {jour: audio_service.getDayStatistics(jour) for jour in jours}
        return render_template('marketing.html', stats_jours=stats_jours)
    except Exception as e:
        print(f"Erreur marketing_dashboard: {e}")
        return render_template('marketing.html', stats_jours={})

# ==================== UPLOAD ====================

@app.route('/marketing/upload/multiple', methods=['POST'])
def marketing_upload_multiple():
    try:
        files = request.files.getlist('files[]')
        jour = request.form.get('jour_semaine', '').upper()

        if not files or not jour:
            return jsonify({'success': False, 'error': "Données manquantes"}), 400

        # Filtrer les fichiers valides
        valid_files = [f for f in files if f.filename and allowed_file(f.filename)]
        
        if not valid_files:
            return jsonify({'success': False, 'error': "Aucun fichier valide"}), 400

        # Déléguer au service (passer app.root_path directement)
        uploaded_count, errors = audio_service.uploadMultipleFiles(
            valid_files, 
            jour, 
            app.root_path,
            id_utilisateur=1
        )

        return jsonify({
            'success': True, 
            'uploaded': uploaded_count,
            'errors': errors
        }), 201

    except Exception as e:
        print(f"Erreur upload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SUPPRESSION ====================

@app.route('/marketing/jour/<jour>/delete', methods=['DELETE'])
def marketing_delete_jour(jour):
    """Supprime tous les fichiers d'un jour"""
    try:
        jour = jour.upper()
        deleted_count = audio_service.deleteDayFilesWithPhysical(jour)

        return jsonify({
            'success': True,
            'count': deleted_count
        }), 200

    except Exception as e:
        print(f"Erreur delete jour: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/marketing/musique/<int:id_fichier>', methods=['DELETE'])
def marketing_delete_musique(id_fichier):
    """Supprime une musique spécifique"""
    try:
        success, error = audio_service.deleteAudioFileWithPhysicalFile(id_fichier)
        
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': error}), 404 if error == 'Fichier introuvable' else 500

    except Exception as e:
        print(f"Erreur delete musique: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== API AUDIO ====================

@app.route('/api/v1/audio/list')
def api_list_audio():
    try:
        jour = request.args.get('jour', '').upper()
        fichiers = audio_service.getAudioFilesByDay(jour) if jour else audio_service.getAllAudioFiles()
        data = audio_service.formatAudioFilesForApi(fichiers)

        return jsonify({'success': True, 'data': data}), 200

    except Exception as e:
        print(f"Erreur api list: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v1/audio/download/<int:id_fichier>')
def api_download_audio(id_fichier):
    """Télécharge un fichier audio"""
    try:
        audio = audio_service.getAudioFileById(id_fichier)

        if not audio:
            return jsonify({'success': False, 'error': 'Fichier introuvable en BDD'}), 404
        
        if not audio.chemin_fichier or not os.path.exists(audio.chemin_fichier):
            return jsonify({'success': False, 'error': f'Fichier physique introuvable: {audio.chemin_fichier}'}), 404

        return send_file(
            audio.chemin_fichier,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f"{audio.nom}.mp3"
        )
    except Exception as e:
        print(f"Erreur download audio: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STATISTIQUES ====================

@app.route('/marketing/stats/semaine')
def marketing_stats_semaine():
    """Retourne les statistiques de toute la semaine"""
    try:
        stats = audio_service.getWeekStatistics()
        return jsonify({'success': True, 'data': stats}), 200

    except Exception as e:
        print(f"Erreur stats semaine: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ORDRE DES FICHIERS ====================

@app.route('/marketing/jour/<jour>/fichiers-ordre')
def marketing_get_fichiers_ordre(jour):
    """Récupère les fichiers d'un jour pour les ordonner"""
    try:
        jour = jour.upper()
        fichiers_data = audio_service.getAudioFilesForOrdering(jour)
        
        return jsonify({
            'success': True,
            'jour': jour,
            'fichiers': fichiers_data
        }), 200
        
    except Exception as e:
        print(f"Erreur get fichiers ordre: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/marketing/jour/<jour>/sauvegarder-ordre', methods=['POST'])
def marketing_save_ordre(jour):
    """Sauvegarde l'ordre des fichiers"""
    try:
        jour = jour.upper()
        data = request.get_json()
        fichiers_ordre = data.get('fichiers_ordre', [])
        
        if not fichiers_ordre:
            return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400
        
        ordre_folder = os.path.join(app.root_path, 'static', 'ordre')
        audio_service.savePlaybackOrder(jour, fichiers_ordre, ordre_folder)
        
        return jsonify({
            'success': True,
            'message': f'Ordre sauvegardé pour {jour} ({len(fichiers_ordre)} fichiers)'
        }), 200
        
    except Exception as e:
        print(f"Erreur save ordre: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PLAYLIST ====================

@app.route('/marketing/playlist/generate/week', methods=['POST'])
def marketing_generate_playlist_week():
    """Génère les playlists M3U en respectant l'ordre sauvegardé"""
    try:
        # Créer le planning
        planning = planning_service.createPlanning(
            nom_planning=f"Planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            date_debut=datetime.now().isoformat(),
            date_fin=datetime.now().isoformat()
        )

        if not planning:
            return jsonify({'success': False, 'error': 'Erreur création planning'}), 500

        # Déléguer toute la logique au service
        playlists_created, errors = playlist_service.generateWeekPlaylistsWithOrder(
            id_planning=planning.id_planning,
            audio_service=audio_service,
            app_root_path=app.root_path,
            use_http_urls=True
        )

        return jsonify({
            'success': True,
            'count': len(playlists_created),
            'data': [p.to_dict() for p in playlists_created],
            'errors': errors if errors else []
        }), 201

    except Exception as e:
        print(f"Erreur génération playlist: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v1/playlist/download/<int:id_playlist>')
def api_download_playlist(id_playlist):
    """Télécharge un fichier M3U"""
    try:
        playlist = playlist_service.getPlaylistById(id_playlist)

        if not playlist:
            return jsonify({'success': False, 'error': 'Playlist introuvable'}), 404
        
        if not playlist.chemin_fichier_m3u or not os.path.exists(playlist.chemin_fichier_m3u):
            return jsonify({'success': False, 'error': 'Fichier M3U introuvable'}), 404

        return send_file(
            playlist.chemin_fichier_m3u,
            mimetype='audio/x-mpegurl',
            as_attachment=True,
            download_name=f"{playlist.nom_playlist}.m3u"
        )
    except Exception as e:
        print(f"Erreur download playlist: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== API JSON PLAYLISTS ====================

@app.route('/api/v1/playlists')
def api_get_all_playlists():
    """Retourne toutes les playlists en JSON"""
    try:
        playlists = playlist_service.getAllPlaylists()
        
        result = []
        for pl in playlists:
            fichiers = playlist_service.getPlaylistAudioFiles(pl.id_playlist)
            
            fichiers_data = []
            for f in fichiers:
                fichiers_data.append({
                    'id': f.id_fichier,
                    'nom': f.nom,
                    'artiste': f.artiste,
                    'album': f.album,
                    'duree': f.duree,
                    'download_url': url_for('api_download_audio', id_fichier=f.id_fichier, _external=True)
                })
            
            result.append({
                'id_playlist': pl.id_playlist,
                'nom_playlist': pl.nom_playlist,
                'jour_semaine': pl.jour_semaine,
                'duree_totale': pl.duree_total,
                'nombre_fichiers': len(fichiers),
                'fichiers': fichiers_data,
                'download_m3u_url': url_for('api_download_playlist', id_playlist=pl.id_playlist, _external=True),
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'playlists': result
        }), 200
        
    except Exception as e:
        print(f"Erreur API playlists: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v1/playlist/<int:id_playlist>')
def api_get_playlist_details(id_playlist):
    """Retourne les détails d'une playlist spécifique en JSON"""
    try:
        playlist = playlist_service.getPlaylistById(id_playlist)
        
        if not playlist:
            return jsonify({'success': False, 'error': 'Playlist introuvable'}), 404
        
        fichiers = playlist_service.getPlaylistAudioFiles(id_playlist)
        
        fichiers_data = []
        for idx, f in enumerate(fichiers, start=1):
            fichiers_data.append({
                'ordre': idx,
                'id': f.id_fichier,
                'nom': f.nom,
                'artiste': f.artiste,
                'album': f.album,
                'duree': f.duree,
                'duree_formattee': f"{f.duree // 60}:{f.duree % 60:02d}" if f.duree else "0:00",
                'taille': f.taille,
                'download_url': url_for('api_download_audio', id_fichier=f.id_fichier, _external=True)
            })
        
        return jsonify({
            'success': True,
            'playlist': {
                'id_playlist': playlist.id_playlist,
                'nom_playlist': playlist.nom_playlist,
                'jour_semaine': playlist.jour_semaine,
                'duree_totale': playlist.duree_total,
                'duree_totale_formattee': f"{playlist.duree_total // 60} minutes",
                'nombre_fichiers': len(fichiers),
                'fichiers': fichiers_data,
                'download_m3u_url': url_for('api_download_playlist', id_playlist=playlist.id_playlist, _external=True),
                'download_zip_url': url_for('api_download_playlist_zip', id_playlist=playlist.id_playlist, _external=True),
                'stream_url': url_for('api_stream_playlist', id_playlist=playlist.id_playlist, _external=True)
            }
        }), 200
        
    except Exception as e:
        print(f"Erreur API playlist detail: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v1/playlists/jour/<jour>')
def api_get_playlists_by_day(jour):
    """Retourne les playlists d'un jour spécifique"""
    try:
        jour = jour.upper()
        all_playlists = playlist_service.getAllPlaylists()
        playlists_jour = [pl for pl in all_playlists if pl.jour_semaine and pl.jour_semaine.upper() == jour]
        
        result = []
        for pl in playlists_jour:
            fichiers = playlist_service.getPlaylistAudioFiles(pl.id_playlist)
            
            fichiers_data = []
            for f in fichiers:
                fichiers_data.append({
                    'id': f.id_fichier,
                    'nom': f.nom,
                    'artiste': f.artiste,
                    'duree': f.duree,
                    'download_url': url_for('api_download_audio', id_fichier=f.id_fichier, _external=True)
                })
            
            result.append({
                'id_playlist': pl.id_playlist,
                'nom_playlist': pl.nom_playlist,
                'duree_totale': pl.duree_total,
                'nombre_fichiers': len(fichiers),
                'fichiers': fichiers_data,
                'download_m3u_url': url_for('api_download_playlist', id_playlist=pl.id_playlist, _external=True)
            })
        
        return jsonify({
            'success': True,
            'jour': jour,
            'count': len(result),
            'playlists': result
        }), 200
        
    except Exception as e:
        print(f"Erreur API playlists jour: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500