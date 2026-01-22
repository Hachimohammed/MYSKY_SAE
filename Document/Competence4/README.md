# EXPLICATION COMPETENCE 4 BASE DE DONNEES

La logique expliquée ci-dessous s'appuie sur notre Modele Entite-Association (MEA) que vous trouverez au fichier MEA.png dans le repertoire.

  Comme point de départ de la base de données, on est parti des **Utilisateurs** ayant tous un nom, prenom, email _(en cas de contact)_, mot de passe et groupe etant soit Admin, soit Marketing, soit Commercial.
  On s'est dit qu'afin d'éviter la redondance, pouvant impliquer des fautes de frappe donc une base de données éronée, il valait mieux avoir les différents groupes stockés dans la table **Groupe_Role** et donner leur clé étrangère aux utilisateurs pour identifier leur groupe.

  L'application consiste à l'ajout de fichier audio par des utilisateurs et afin de garder une trace de ces ajouts, on devait relier la table **Fichier_Audio** à **Utilisateur** par la table **Ajoute** qui prend comme clés primaires etrangeres les clés de **Utilisateur** et **Fichier_Audio** avec la date d'ajout.

  Les fichiers audio sont soit des musiques, soit des annonnces (pubs, urgence...), c'est pourquoi à la même image que **Groupe_Role**, on a relié **Fichier_Audio** à **Type_contenu**.

  L'enjeu était d'ensuite relier ces fichiers à des playlists. C'est pourquoi on a créé la table **Playlist** et **Fait_partie_de** qui recevra comme clé étrangère primaire*id_playlist* et *id_fichier_audio* afin que chaque musique soit associée à une ou plusieurs playlists.

  Maintenant, du au fait que l'application est faite pour qu'un planning recoive des playlist, il fallait desormais relier la table **Planning** à **Playlist** par playlist qui recoit comme clé étrangère *id_planning* pour être associé à un planning généré par l'application.

  Enfin, il reste la partie des **Lecteurs** qui sont reliés à des playlists qu'ils vont lire par la table **joue_dans** afin qu'un lecteur puisse jouer plusieurs playlists et plusieurs lecteurs jouent une même playlist. **Lecteur** est ensuite relié à **Log** pour son état et **Localisation** pour sa position.

  
