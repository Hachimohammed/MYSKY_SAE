import sqlite3
import os
from datetime import datetime
from flask import url_for, request
from app import app
from app.models.Playlist import Playlist
from app.models.PlaylistDAOInterface import PlaylistDAOInterface

class PlaylistDAO(PlaylistDAOInterface):
	"""DAO pour la gestion des playlists M3U"""
	
	def __init__(self):
		self.database = app.root_path + '/musicapp.db'
		self.playlist_folder = os.path.join(app.root_path, 'static', 'playlists')
		os.makedirs(self.playlist_folder, exist_ok=True)
	
	def _getDbConnection(self):
		"""Obtient une connexion à la base de données"""
		conn = sqlite3.connect(self.database)
		conn.execute("PRAGMA foreign_keys = ON;")
		conn.row_factory = sqlite3.Row
		return conn
	
	def create(self, nom_playlist, chemin_fichier_m3u, duree_total=0, id_planning=None, jour_semaine=None):
		"""Crée une nouvelle playlist M3U"""
		try:
			conn = self._getDbConnection()
			date_creation = datetime.now().isoformat()
			
			cursor = conn.execute("""
				INSERT INTO playlist (nom_playlist, chemin_fichier_m3u, duree_total, id_planning)
				VALUES (?, ?, ?, ?)
			""", (nom_playlist, chemin_fichier_m3u, duree_total, id_planning))
			
			id_playlist = cursor.lastrowid
			conn.commit()
			conn.close()
			
			return Playlist({
				'id_playlist': id_playlist,
				'nom_playlist': nom_playlist,
				'chemin_fichier_m3u': chemin_fichier_m3u,
				'duree_total': duree_total,
				'id_planning': id_planning,
				'jour_semaine': jour_semaine,
				'date_creation': date_creation
			})
		except Exception as e:
			print(f"Erreur dans create: {e}")
			return None
	
	def getById(self, id_playlist):
		"""Récupère une playlist par son ID"""
		try:
			conn = self._getDbConnection()
			row = conn.execute(
				"SELECT * FROM playlist WHERE id_playlist = ?",
				(id_playlist,)
			).fetchone()
			conn.close()
			
			if row:
				return Playlist(dict(row))
			return None
		except Exception as e:
			print(f"Erreur dans getById: {e}")
			return None
	
	def getAll(self):
		"""Récupère toutes les playlists"""
		try:
			conn = self._getDbConnection()
			rows = conn.execute("""
				SELECT * FROM playlist
				ORDER BY id_playlist DESC
			""").fetchall()
			conn.close()
			
			return [Playlist(dict(row)) for row in rows]
		except Exception as e:
			print(f"Erreur dans getAll: {e}")
			return []
	
	def getByPlanning(self, id_planning):
		"""Récupère les playlists d'un planning"""
		try:
			conn = self._getDbConnection()
			rows = conn.execute("""
				SELECT * FROM playlist
				WHERE id_planning = ?
				ORDER BY nom_playlist
			""", (id_planning,)).fetchall()
			conn.close()
			
			return [Playlist(dict(row)) for row in rows]
		except Exception as e:
			print(f"Erreur dans getByPlanning: {e}")
			return []
	
	def getByDay(self, jour_semaine):
		"""Récupère la playlist d'un jour spécifique"""
		try:
			conn = self._getDbConnection()
			row = conn.execute("""
				SELECT * FROM playlist
				WHERE nom_playlist LIKE ?
				ORDER BY id_playlist DESC
				LIMIT 1
			""", (f"%{jour_semaine}%",)).fetchone()
			conn.close()
			
			if row:
				return Playlist(dict(row))
			return None
		except Exception as e:
			print(f"Erreur dans getByDay: {e}")
			return None
	
	def update(self, id_playlist, nom_playlist, duree_total):
		"""Met à jour une playlist"""
		try:
			conn = self._getDbConnection()
			conn.execute("""
				UPDATE playlist
				SET nom_playlist = ?, duree_total = ?
				WHERE id_playlist = ?
			""", (nom_playlist, duree_total, id_playlist))
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			print(f"Erreur dans update: {e}")
			return False
	
	def delete(self, id_playlist):
		"""Supprime une playlist"""
		try:
			conn = self._getDbConnection()
			conn.execute("DELETE FROM fait_partie_de WHERE id_playlist = ?", (id_playlist,))
			conn.execute("DELETE FROM joue_dans WHERE id_playlist = ?", (id_playlist,))
			conn.execute("DELETE FROM playlist WHERE id_playlist = ?", (id_playlist,))
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			print(f"Erreur dans delete: {e}")
			return False
	
	def addAudioFile(self, id_playlist, id_fichier):
		"""Ajoute un fichier audio à une playlist"""
		try:
			conn = self._getDbConnection()
			conn.execute("""
				INSERT OR IGNORE INTO fait_partie_de (id_Fichier_audio, id_playlist)
				VALUES (?, ?)
			""", (id_fichier, id_playlist))
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			print(f"Erreur dans addAudioFile: {e}")
			return False
	
	def removeAudioFile(self, id_playlist, id_fichier):
		"""Retire un fichier audio d'une playlist"""
		try:
			conn = self._getDbConnection()
			conn.execute("""
				DELETE FROM fait_partie_de
				WHERE id_Fichier_audio = ? AND id_playlist = ?
			""", (id_fichier, id_playlist))
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			print(f"Erreur dans removeAudioFile: {e}")
			return False
	
	def getAudioFiles(self, id_playlist):
		"""Récupère tous les fichiers audio d'une playlist"""
		try:
			conn = self._getDbConnection()
			rows = conn.execute("""
				SELECT f.*
				FROM Fichier_audio f
				INNER JOIN fait_partie_de fp ON f.id_Fichier_audio = fp.id_Fichier_audio
				WHERE fp.id_playlist = ?
				ORDER BY f.nom
			""", (id_playlist,)).fetchall()
			conn.close()
			
			from app.models.AudioFile import AudioFile
			return [AudioFile(dict(row)) for row in rows]
		except Exception as e:
			print(f"Erreur dans getAudioFiles: {e}")
			return []
	
	def generateM3U(self, id_playlist, use_http_urls=True):
		"""
		Génère le fichier M3U physique pour une playlist
		
		Args:
			id_playlist: ID de la playlist
			use_http_urls: Si True, génère des URLs HTTP, sinon des chemins locaux
		"""
		try:
			playlist = self.getById(id_playlist)
			if not playlist:
				print(f"Playlist {id_playlist} introuvable")
				return False
			
			audio_files = self.getAudioFiles(id_playlist)
			
			if not audio_files:
				print(f"Aucun fichier audio dans la playlist {id_playlist}")
				return False
			
			m3u_path = playlist.chemin_fichier_m3u
			os.makedirs(os.path.dirname(m3u_path), exist_ok=True)
			
			print(f"Génération M3U: {m3u_path}")
			print(f"Nombre de fichiers: {len(audio_files)}")
			print(f"Mode: {'URLs HTTP' if use_http_urls else 'Chemins locaux'}")
			
			with open(m3u_path, 'w', encoding='utf-8') as f:
				f.write("#EXTM3U\n")
				f.write(f"# Playlist: {playlist.nom_playlist}\n")
				f.write(f"# Générée le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
				
				for audio in audio_files:
					duree = audio.duree if audio.duree else -1
					
					
					if audio.artiste and audio.artiste != 'Inconnu':
						titre = f"{audio.artiste} - {audio.nom}"
					else:
						titre = audio.nom
					
					f.write(f"#EXTINF:{duree},{titre}\n")
					
					# IMPORTANT : Générer l'URL HTTP pour que le lecteur puisse streamer
					if use_http_urls:
						# Générer l'URL de téléchargement
						with app.app_context():
							audio_url = url_for(
								'api_download_audio',
								id_fichier=audio.id_fichier,
								_external=True
							)
						f.write(f"{audio_url}\n")
					else:
						# Utiliser le chemin local (ne marchera que si les fichiers sont accessibles)
						f.write(f"{audio.chemin_fichier}\n")
			
			print(f"Fichier M3U généré avec succès: {m3u_path}")
			return True
			
		except Exception as e:
			print(f"Erreur dans generateM3U: {e}")
			import traceback
			traceback.print_exc()
			return False
	
	def generateM3UForDay(self, jour_semaine, id_planning=None, use_http_urls=True):
		"""Génère une playlist M3U pour un jour de la semaine"""
		try:
			from app.models.AudioFileDAO import AudioFileDAO
			audio_dao = AudioFileDAO()
			
			audio_files = audio_dao.getByDay(jour_semaine)
			
			if not audio_files:
				print(f"Aucun fichier audio pour {jour_semaine}")
				return None
			
			nom_playlist = f"Playlist_{jour_semaine}_{datetime.now().strftime('%Y%m%d')}"
			chemin_m3u = os.path.join(self.playlist_folder, f"{nom_playlist}.m3u")
			
			duree_totale = sum(audio.duree for audio in audio_files if audio.duree)
			
			playlist = self.create(nom_playlist, chemin_m3u, duree_totale, id_planning, jour_semaine)
			
			if not playlist:
				print("Erreur création playlist en BDD")
				return None
			
			for audio in audio_files:
				self.addAudioFile(playlist.id_playlist, audio.id_fichier)
			
			if self.generateM3U(playlist.id_playlist, use_http_urls=use_http_urls):
				print(f"Playlist {jour_semaine} générée: {playlist.id_playlist}")
				return playlist
			else:
				print(f"Erreur génération M3U pour {jour_semaine}")
				return None
				
		except Exception as e:
			print(f"Erreur dans generateM3UForDay: {e}")
			import traceback
			traceback.print_exc()
			return None
	
	def generateWeeklyM3U(self, id_planning, use_http_urls=True):
		"""Génère toutes les playlists M3U de la semaine"""
		try:
			jours = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
			playlists = []
			
			for jour in jours:
				playlist = self.generateM3UForDay(jour, id_planning, use_http_urls)
				if playlist:
					playlists.append(playlist)
				else:
					print(f"Pas de playlist générée pour {jour}")
			
			return playlists
		except Exception as e:
			print(f"Erreur dans generateWeeklyM3U: {e}")
			return []
	
	def assignToPlayer(self, id_playlist, id_lecteur, date_diffusion):
		"""Assigne une playlist à un lecteur (table joue_dans)"""
		try:
			conn = self._getDbConnection()
			conn.execute("""
				INSERT OR REPLACE INTO joue_dans (id_playlist, id_lecteur, date_diffusion)
				VALUES (?, ?, ?)
			""", (id_playlist, id_lecteur, date_diffusion))
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			print(f"Erreur dans assignToPlayer: {e}")
			return False
	
	def getPlayersForPlaylist(self, id_playlist):
		"""Récupère les lecteurs assignés à une playlist"""
		try:
			conn = self._getDbConnection()
			rows = conn.execute("""
				SELECT l.*, jd.date_diffusion
				FROM lecteur l
				INNER JOIN joue_dans jd ON l.id_lecteur = jd.id_lecteur
				WHERE jd.id_playlist = ?
			""", (id_playlist,)).fetchall()
			conn.close()
			
			return [dict(row) for row in rows]
		except Exception as e:
			print(f"Erreur dans getPlayersForPlaylist: {e}")
			return []
	
	def getDownloadUrl(self, id_playlist):
		"""Génère l'URL de téléchargement du fichier M3U pour l'API"""
		return f"/api/v1/playlist/download/{id_playlist}"
	
	def addAudioFileWithOrder(self, id_playlist, id_fichier, ordre):
		"""Ajoute un fichier audio à une playlist avec un ordre spécifique"""
		try:
			conn = self._getDbConnection()
			conn.execute("""
				INSERT OR REPLACE INTO fait_partie_de (id_Fichier_audio, id_playlist, ordre)
				VALUES (?, ?, ?)
			""", (id_fichier, id_playlist, ordre))
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			print(f"Erreur dans addAudioFileWithOrder: {e}")
			return False

	def updateAudioOrder(self, id_playlist, fichiers_ordonnes):
		"""
		Met à jour l'ordre des fichiers dans une playlist
		fichiers_ordonnes : liste de tuples (id_fichier, ordre)
		"""
		try:
			conn = self._getDbConnection()
			
			for id_fichier, ordre in fichiers_ordonnes:
				conn.execute("""
					UPDATE fait_partie_de
					SET ordre = ?
					WHERE id_Fichier_audio = ? AND id_playlist = ?
				""", (ordre, id_fichier, id_playlist))
			
			conn.commit()
			conn.close()
			return True
		except Exception as e:
			print(f"Erreur dans updateAudioOrder: {e}")
			return False

	def getAudioFiles(self, id_playlist):
		"""Récupère tous les fichiers audio d'une playlist TRIÉS PAR ORDRE"""
		try:
			conn = self._getDbConnection()
			rows = conn.execute("""
				SELECT f.*, fp.ordre
				FROM Fichier_audio f
				INNER JOIN fait_partie_de fp ON f.id_Fichier_audio = fp.id_Fichier_audio
				WHERE fp.id_playlist = ?
				ORDER BY fp.ordre ASC, f.nom ASC
			""", (id_playlist,)).fetchall()
			conn.close()
			
			from app.models.AudioFile import AudioFile
			return [AudioFile(dict(row)) for row in rows]
		except Exception as e:
			print(f"Erreur dans getAudioFiles: {e}")
			return []