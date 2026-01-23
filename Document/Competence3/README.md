# COMPETENCE 3 RESEAU
La vidéo de démonstration présentée le jour de la soutenance est disponible à l’adresse suivante :  
https://www.youtube.com/watch?v=FTaKeE_loNI

# Equipement Réseaux adéquates aux projets

Deux VM Linux,distribution de votre choix (comme vous voulez pour le choix de celle-ci on à pris Linux Lubuntu c'est léger pour virtualiser)

Le projet à été réalisés sous une configuration tailscale (liaison en continue,pas besoin de passer par le FAI,ou de rester en local choix portés sur le fait d'ajouter 
automatiquement des machines)

SSH configurer à l'aide de tailscale 'tailscale set --ssh' 

Rsync deja pre-installer avec Lubuntu (et surement avec la plupart des distro basée sur Debian)

mpd (partie démon) mpc (partie lecture)
```
Configuration Server:
"music_directory     "/home/servermysky/MYSKY_SAE/PagesCodes/Sae_V2/app/static/audio"
playlist_directory  "/home/servermysky/MYSKY_SAE/PagesCodes/Sae_V2/app/static/playlists"
db_file             "/var/lib/mpd/tag_cache"
state_file          "/var/lib/mpd/state"
log_file            "/var/log/mpd/mpd.log"
pid_file            "/run/mpd/pid"
user                "servermysky"
group               "servermysky"

bind_to_address     "127.0.0.1"
port                "6600"
```

```
Configuration Clients :

music_directory    "/home/test/Musique"
playlist_directory    "/home/test/playlists"
db_file    "/var/lib/mpd/tag_cache"
log_file    "/var/log/mpd/mpd.log"
pid_file    "/run/mpd/pid"
state_file    "/var/lib/mpd/state"
sticker_file    "/var/lib/mpd/sticker.sql"

user "test"
group "test"

bind_to_address    0.0.0.0
port    6600

audio_output {
    type    "alsa"
    name    "ALSA Output"
    device    "default"
    mixer_type  "software"
```

Toutes les fonctions de 'lecteurDAO.py' ont nécessiter interventions de ses technologies et de mes configuration

