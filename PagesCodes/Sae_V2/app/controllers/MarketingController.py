from flask import (
    render_template, request, jsonify, send_file,
    redirect, url_for, flash
)
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from mutagen.mp3 import MP3

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

audio_service = AudioFileService()
playlist_service = PlaylistService()
planning_service = PlanningService()

# ==================== UTILS ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_mp3_metadata(filepath):
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

# ==================== PAGE PRINCIPALE ====================

@app.route('/marketing')
@app.route('/marketing/dashboard')
def marketing_dashboard():
    try:
        jours = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI',
                 'VENDREDI', 'SAMEDI', 'DIMANCHE']
        stats_jours = {}

        for jour in jours:
            fichiers = audio_service.getAudioFilesByDay(jour)
            stats_jours[jour] = {
                'count': len(fichiers),
                'duree_totale': sum(f.duree for f in fichiers if f.duree),
                'taille_totale': sum(f.taille for f in fichiers if f.taille)
            }

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

        uploaded_count = 0
        errors = []

        for file in files:
            if file.filename == '' or not allowed_file(file.filename):
                continue

            filename = secure_filename(file.filename)

            folder_relative = os.path.join('static', 'audio', jour)
            folder_full = os.path.join(app.root_path, folder_relative)
            os.makedirs(folder_full, exist_ok=True)
            path_full = os.path.join(folder_full, filename)
            file.save(path_full)
            meta = get_mp3_metadata(path_full)

       
            audio = audio_service.createAudioFile(
                nom=meta['titre'] or filename.rsplit('.', 1)[0],
                type_fichier='mp3',
                taille=os.path.getsize(path_full),
                chemin_fichier=path_full,
                id_type_contenu=1,
                duree=meta['duree'],
                artiste=meta['artiste'],
                album=meta['album'],
                jour_semaine=jour,
                id_utilisateur=1
            )

            if audio:
                uploaded_count += 1
            else:
                errors.append(f"Erreur BDD pour {filename}")
                if os.path.exists(path_full): 
                    os.remove(path_full)

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
        fichiers = audio_service.getAudioFilesByDay(jour)
        
        deleted_count = 0

        for f in fichiers:
            
            if f.chemin_fichier and os.path.exists(f.chemin_fichier):
                try:
                    os.remove(f.chemin_fichier)
                    print(f"Fichier supprimé: {f.chemin_fichier}")
                except Exception as e:
                    print(f"Erreur suppression fichier {f.chemin_fichier}: {e}")
            
            #
            if audio_service.deleteAudioFile(f.id_fichier):
                deleted_count += 1

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
        audio = audio_service.getAudioFileById(id_fichier)
        
        if not audio:
            return jsonify({'success': False, 'error': 'Fichier introuvable'}), 404

        if audio.chemin_fichier and os.path.exists(audio.chemin_fichier):
            try:
                os.remove(audio.chemin_fichier)
                print(f"Fichier supprimé: {audio.chemin_fichier}")
            except Exception as e:
                print(f"Erreur suppression fichier: {e}")

      
        if audio_service.deleteAudioFile(id_fichier):
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': 'Erreur suppression BDD'}), 500

    except Exception as e:
        print(f"Erreur delete musique: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== API AUDIO ====================

@app.route('/api/v1/audio/list')
def api_list_audio():
    try:
        jour = request.args.get('jour', '').upper()
        fichiers = audio_service.getAudioFilesByDay(jour) if jour else audio_service.getAllAudioFiles()

        data = []
        for f in fichiers:
            d = f.to_dict()
            d['download_url'] = url_for(
                'api_download_audio',
                id_fichier=f.id_fichier,
                _external=True
            )
            data.append(d)

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
        jours = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
        
        stats_par_jour = {}
        total_musiques = 0
        total_duree = 0
        total_taille = 0

        for jour in jours:
            fichiers = audio_service.getAudioFilesByDay(jour)
            duree_jour = sum(f.duree for f in fichiers if f.duree)
            taille_jour = sum(f.taille for f in fichiers if f.taille)
            
            stats_par_jour[jour] = {
                'nombre_musiques': len(fichiers),
                'duree_totale': duree_jour,
                'taille_totale': taille_jour
            }
            
            total_musiques += len(fichiers)
            total_duree += duree_jour
            total_taille += taille_jour

        return jsonify({
            'success': True,
            'data': {
                'par_jour': stats_par_jour,
                'totaux': {
                    'nombre_musiques': total_musiques,
                    'duree_totale': total_duree,
                    'taille_totale': total_taille
                }
            }
        }), 200

    except Exception as e:
        print(f"Erreur stats semaine: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PLAYLIST ====================

@app.route('/marketing/playlist/generate/week', methods=['POST'])
def marketing_generate_playlist_week():
    """Génère les playlists M3U EN RESPECTANT L'ORDRE sauvegardé"""
    try:
        jours = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
        
        planning = planning_service.createPlanning(
            nom_planning=f"Planning_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            date_debut=datetime.now().isoformat(),
            date_fin=datetime.now().isoformat()
        )

        if not planning:
            return jsonify({'success': False, 'error': 'Erreur création planning'}), 500

        playlists_created = []
        
        import json
        ordre_folder = os.path.join(app.root_path, 'static', 'ordre')
        
        for jour in jours:
           
            ordre_file = os.path.join(ordre_folder, f"ordre_{jour}.json")
            fichiers_ordonnes = []
            
            if os.path.exists(ordre_file):
               
                with open(ordre_file, 'r', encoding='utf-8') as f:
                    ordre_data = json.load(f)
                    fichiers_ids = ordre_data.get('fichiers_ordre', [])
                    
                   
                    for id_fichier in fichiers_ids:
                        audio = audio_service.getAudioFileById(id_fichier)
                        if audio:
                            fichiers_ordonnes.append(audio)
                    
                    print(f"📋 Ordre trouvé pour {jour}: {len(fichiers_ordonnes)} fichiers")
            else:
               
                fichiers_ordonnes = audio_service.getAudioFilesByDay(jour)
                print(f" Pas d'ordre pour {jour}, utilisation ordre par défaut")
            
            if not fichiers_ordonnes:
                print(f" Aucun fichier pour {jour}")
                continue
            
            # Créer la playlist via le service
            nom_playlist = f"Playlist_{jour}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            chemin_m3u = os.path.join(app.root_path, 'static', 'playlists', f"{nom_playlist}.m3u")
            
            duree_totale = sum(f.duree for f in fichiers_ordonnes if f.duree)
            
            playlist = playlist_service.createPlaylist(
                nom_playlist=nom_playlist,
                chemin_fichier_m3u=chemin_m3u,
                duree_total=duree_totale,
                id_planning=planning.id_planning,
                jour_semaine=jour
            )
            
            if not playlist:
                print(f" Erreur création playlist pour {jour}")
                continue
            
            
            for ordre, fichier in enumerate(fichiers_ordonnes, start=1):
                playlist_service.addAudioWithOrder(playlist.id_playlist, fichier.id_fichier, ordre)
            
          
            if playlist_service.generateM3UFile(playlist.id_playlist, use_http_urls=True):
                playlists_created.append(playlist)
                print(f" Playlist générée pour {jour} avec {len(fichiers_ordonnes)} fichiers")

        return jsonify({
            'success': True,
            'count': len(playlists_created),
            'data': [p.to_dict() for p in playlists_created]
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

@app.route('/marketing/jour/<jour>/fichiers-ordre')
def marketing_get_fichiers_ordre(jour):
    """Récupère les fichiers d'un jour pour les ordonner"""
    try:
        jour = jour.upper()
        fichiers = audio_service.getAudioFilesByDay(jour)
        
        fichiers_data = []
        for f in fichiers:
            fichiers_data.append({
                'id': f.id_fichier,
                'nom': f.nom,
                'artiste': f.artiste or 'Inconnu',
                'duree': f.duree or 0,
                'duree_formattee': f"{f.duree // 60}:{f.duree % 60:02d}" if f.duree else "0:00"
            })
        
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
    """Sauvegarde UNIQUEMENT l'ordre des fichiers dans la BDD"""
    try:
        jour = jour.upper()
        data = request.get_json()
        
        fichiers_ordre = data.get('fichiers_ordre', [])
        
        if not fichiers_ordre:
            return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400
        
        print(f" Sauvegarde ordre pour {jour}: {len(fichiers_ordre)} fichiers")
       
        import json
        ordre_folder = os.path.join(app.root_path, 'static', 'ordre')
        os.makedirs(ordre_folder, exist_ok=True)
        
        ordre_file = os.path.join(ordre_folder, f"ordre_{jour}.json")
        
        with open(ordre_file, 'w', encoding='utf-8') as f:
            json.dump({
                'jour': jour,
                'fichiers_ordre': fichiers_ordre,
                'date_sauvegarde': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f" Ordre sauvegardé dans {ordre_file}")
        
        return jsonify({
            'success': True,
            'message': f'Ordre sauvegardé pour {jour} ({len(fichiers_ordre)} fichiers)'
        }), 200
        
    except Exception as e:
        print(f"Erreur save ordre: {e}")
        import traceback
        traceback.print_exc()
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