const API_BASE = window.location.origin;

    
    let currentPlanifierJour = '';
    let fichiersOrdre = [];
    let draggedElement = null;

    
    function showUploadModal(jour) {
        document.getElementById('uploadModalTitle').textContent = `Ajouter des musiques - ${jour}`;
        document.getElementById('jour_upload').value = jour;
        document.getElementById('fileInput').value = '';
        document.getElementById('uploadProgress').classList.add('hidden');
        document.getElementById('uploadModal').classList.add('active');
    }

    function closeUploadModal() {
        document.getElementById('uploadModal').classList.remove('active');
    }


    async function uploadFiles() {
        const fileInput = document.getElementById('fileInput');
        const jour = document.getElementById('jour_upload').value;
        const files = fileInput.files;

        if (files.length === 0) {
            alert('Veuillez sélectionner au moins un fichier MP3');
            return;
        }

        const formData = new FormData();
        formData.append('jour_semaine', jour);
        
        for (let file of files) {
            formData.append('files[]', file);
        }

        document.getElementById('uploadProgress').classList.remove('hidden');
        document.getElementById('progressBar').style.width = '50%';

        try {
            const response = await fetch(`${API_BASE}/marketing/upload/multiple`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            document.getElementById('progressBar').style.width = '100%';

            if (data.success) {
                alert(`${data.uploaded} fichier(s) téléchargé(s) avec succès!`);
                if (data.errors && data.errors.length > 0) {
                    console.log('Erreurs:', data.errors);
                }
                closeUploadModal();
                location.reload();
            } else {
                alert('Erreur lors du téléchargement: ' + data.error);
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors du téléchargement des fichiers');
        } finally {
            document.getElementById('uploadProgress').classList.add('hidden');
        }
    }

    
    async function showDetails(jour) {
        const modal = document.getElementById('detailsModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalDescription = document.getElementById('modalDescription');
        const mp3List = document.getElementById('mp3List');
        
        modalTitle.textContent = `Détails - ${jour}`;
        modalDescription.textContent = 'Chargement...';
        mp3List.innerHTML = '';
        modal.classList.add('active');

        try {
            const response = await fetch(`${API_BASE}/api/v1/audio/list?jour=${jour}`);
            const data = await response.json();

            if (data.success && data.data.length > 0) {
                modalDescription.textContent = 'Cliquez sur une musique pour voir ses informations détaillées :';
                
                mp3List.innerHTML = data.data.map((fichier, index) => `
                    <div onclick='showMp3Details(${JSON.stringify(fichier)})' class="bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-5 border-2 border-purple-200 hover:border-purple-400 transition-all hover:shadow-lg cursor-pointer">
                        <div class="flex items-center justify-between gap-4">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center flex-shrink-0">
                                    <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                                    </svg>
                                </div>
                                <div>
                                    <h4 class="text-lg font-bold text-gray-900">${fichier.nom}</h4>
                                    <p class="text-sm text-gray-600">${fichier.artiste || 'Inconnu'}</p>
                                </div>
                            </div>
                            <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                            </svg>
                        </div>
                    </div>
                `).join('');
            } else {
                modalDescription.textContent = '';
                mp3List.innerHTML = '<p class="text-gray-500 italic">Aucune musique disponible pour ce jour</p>';
            }
        } catch (error) {
            console.error('Erreur:', error);
            modalDescription.textContent = '';
            mp3List.innerHTML = '<p class="text-red-500">Erreur lors du chargement des données</p>';
        }
    }

    function showMp3Details(fichier) {
        const modalTitle = document.getElementById('modalTitle');
        const modalDescription = document.getElementById('modalDescription');
        const mp3List = document.getElementById('mp3List');
        
        modalTitle.textContent = `Informations - ${fichier.nom}`;
        modalDescription.textContent = '';
        
        const dureeMin = Math.floor(fichier.duree / 60);
        const dureeSec = fichier.duree % 60;
        const tailleMB = (fichier.taille / (1024 * 1024)).toFixed(2);
        
        mp3List.innerHTML = `
            <div class="bg-gradient-to-r from-purple-50 to-purple-100 rounded-2xl p-8 border-2 border-purple-200">
                <div class="flex items-start gap-6 mb-6">
                    <div class="w-20 h-20 bg-purple-500 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg">
                        <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <h4 class="text-2xl font-bold text-gray-900 mb-2">${fichier.nom}</h4>
                        <p class="text-gray-700 text-base mb-3">${fichier.artiste || 'Artiste inconnu'}</p>
                        <span class="inline-block px-3 py-1 bg-purple-200 text-purple-800 rounded-full text-sm font-semibold">${fichier.album || 'Album inconnu'}</span>
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4 bg-white rounded-xl p-5">
                    <div class="flex flex-col">
                        <span class="text-gray-500 text-sm font-medium mb-1">Type</span>
                        <span class="text-gray-900 font-bold text-lg">${fichier.type_fichier.toUpperCase()}</span>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-gray-500 text-sm font-medium mb-1">Durée</span>
                        <span class="text-gray-900 font-bold text-lg">${dureeMin}:${dureeSec.toString().padStart(2, '0')}</span>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-gray-500 text-sm font-medium mb-1">Taille</span>
                        <span class="text-gray-900 font-bold text-lg">${tailleMB} MB</span>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-gray-500 text-sm font-medium mb-1">Date d'ajout</span>
                        <span class="text-gray-900 font-bold text-lg">${new Date(fichier.date_ajout).toLocaleDateString('fr-FR')}</span>
                    </div>
                </div>
                
                <div class="mt-6 flex gap-3">
                    <a href="${fichier.download_url}" class="flex-1 py-3 bg-green-500 hover:bg-green-600 text-white font-bold rounded-xl text-center transition-colors">
                        Télécharger
                    </a>
                    <button onclick="confirmDeleteMp3(${fichier.id_fichier}, '${fichier.nom}')" class="px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-bold rounded-xl transition-colors">
                        Supprimer
                    </button>
                </div>
            </div>
        `;
    }

    async function confirmDeleteMp3(id, nom) {
        if (!confirm(`Êtes-vous sûr de vouloir supprimer "${nom}" ?`)) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/marketing/musique/${id}`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (data.success) {
                alert('Musique supprimée avec succès');
                closeModal();
                location.reload();
            } else {
                alert('Erreur lors de la suppression: ' + data.error);
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors de la suppression');
        }
    }

    async function deleteMp3(jour) {
        if (!confirm(`Êtes-vous sûr de vouloir supprimer TOUTES les musiques de ${jour} ?`)) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/marketing/jour/${jour}/delete`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (data.success) {
                alert(`${data.count} musique(s) supprimée(s) avec succès`);
                location.reload();
} else {
alert('Erreur lors de la suppression: ' + data.error);
}
} catch (error) {
console.error('Erreur:', error);
alert('Erreur lors de la suppression');
}
}
function closeModal() {
    document.getElementById('detailsModal').classList.remove('active');
}


async function showPlanifier(jour) {
    currentPlanifierJour = jour;
    document.getElementById('planifierJour').textContent = `Organisez l'ordre de lecture pour ${jour}`;
    
    // Réinitialiser les champs de date et heure
    document.getElementById('dateDiffusion').value = '';
    document.getElementById('heureDiffusion').value = '';
    
    try {
        const response = await fetch(`${API_BASE}/marketing/jour/${jour}/fichiers-ordre`);
        const data = await response.json();
        
        if (data.success) {
            fichiersOrdre = data.fichiers;
            renderFichiersOrdre();
            document.getElementById('planifierModal').classList.add('active');
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors du chargement des fichiers');
    }
}

function closePlanifierModal() {
    document.getElementById('planifierModal').classList.remove('active');
}


function renderFichiersOrdre() {
    const container = document.getElementById('fichiersOrdreListe');
    
    if (fichiersOrdre.length === 0) {
        container.innerHTML = '<p class="text-gray-500 italic text-center py-8">Aucun fichier disponible</p>';
        return;
    }
    
    container.innerHTML = fichiersOrdre.map((fichier, index) => `
        <div 
            class="fichier-item bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-5 border-2 border-purple-200"
            draggable="true"
            data-id="${fichier.id}"
            data-index="${index}"
            ondragstart="handleDragStart(event)"
            ondragover="handleDragOver(event)"
            ondrop="handleDrop(event)"
            ondragend="handleDragEnd(event)"
            ondragenter="handleDragEnter(event)"
            ondragleave="handleDragLeave(event)"
        >
            <div class="flex items-center gap-4">
                <!-- Numéro d'ordre -->
                <div class="flex-shrink-0">
                    <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center shadow-lg">
                        <span class="text-white text-xl font-bold">${index + 1}</span>
                    </div>
                </div>
                
                <!-- Icône drag -->
                <div class="flex-shrink-0 text-purple-400">
                    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
                    </svg>
                </div>
                
                <!-- Info fichier -->
                <div class="flex-1">
                    <h4 class="text-lg font-bold text-gray-900">${fichier.nom}</h4>
                    <p class="text-sm text-gray-600">${fichier.artiste} • ${fichier.duree_formattee}</p>
                </div>
                
                <!-- Boutons de contrôle -->
                <div class="flex gap-2">
                    <button 
                        onclick="moveUp(${index}); event.stopPropagation();" 
                        class="w-10 h-10 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors flex items-center justify-center"
                        ${index === 0 ? 'disabled style="opacity: 0.3; cursor: not-allowed;"' : ''}
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                        </svg>
                    </button>
                    <button 
                        onclick="moveDown(${index}); event.stopPropagation();" 
                        class="w-10 h-10 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors flex items-center justify-center"
                        ${index === fichiersOrdre.length - 1 ? 'disabled style="opacity: 0.3; cursor: not-allowed;"' : ''}
                    >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}


function moveUp(index) {
    if (index > 0) {
        const temp = fichiersOrdre[index];
        fichiersOrdre[index] = fichiersOrdre[index - 1];
        fichiersOrdre[index - 1] = temp;
        renderFichiersOrdre();
    }
}


function moveDown(index) {
    if (index < fichiersOrdre.length - 1) {
        const temp = fichiersOrdre[index];
        fichiersOrdre[index] = fichiersOrdre[index + 1];
        fichiersOrdre[index + 1] = temp;
        renderFichiersOrdre();
    }
}


function handleDragStart(e) {
    draggedElement = e.target;
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target.innerHTML);
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    if (e.target.classList.contains('fichier-item') && e.target !== draggedElement) {
        e.target.classList.add('drag-over');
    }
}

function handleDragLeave(e) {
    if (e.target.classList.contains('fichier-item')) {
        e.target.classList.remove('drag-over');
    }
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedElement !== e.target && e.target.classList.contains('fichier-item')) {
        const draggedIndex = parseInt(draggedElement.getAttribute('data-index'));
        const targetIndex = parseInt(e.target.getAttribute('data-index'));
        
        
        const draggedItem = fichiersOrdre[draggedIndex];
        fichiersOrdre.splice(draggedIndex, 1);
        fichiersOrdre.splice(targetIndex, 0, draggedItem);
        
        renderFichiersOrdre();
    }
    
    return false;
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    document.querySelectorAll('.fichier-item').forEach(item => {
        item.classList.remove('drag-over');
    });
}


async function savePlanification() {
    if (fichiersOrdre.length === 0) {
        alert('Aucun fichier à sauvegarder');
        return;
    }
    
    
    const dateDiffusion = document.getElementById('dateDiffusion').value;
    const heureDiffusion = document.getElementById('heureDiffusion').value;
    
    
    if (!dateDiffusion || !heureDiffusion) {
        alert(' Veuillez saisir la date et l\'heure de diffusion');
        return;
    }
    
    
    const datetimeDiffusion = `${dateDiffusion} ${heureDiffusion}`;
    
    if (!confirm(` Sauvegarder l'ordre de lecture pour ${currentPlanifierJour} ?\n\n${fichiersOrdre.length} fichiers seront ordonnés.\n Date de diffusion: ${dateDiffusion}\n  Heure de diffusion: ${heureDiffusion}\n\nVous devrez ensuite cliquer sur "Générer playlist" pour créer les fichiers M3U.`)) {
        return;
    }
    
    try {
        const fichiersIds = fichiersOrdre.map(f => f.id);
        
        const response = await fetch(`${API_BASE}/marketing/jour/${currentPlanifierJour}/sauvegarder-ordre`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fichiers_ordre: fichiersIds,
                date_diffusion: dateDiffusion,
                heure_diffusion: heureDiffusion,
                datetime_diffusion: datetimeDiffusion
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(` Ordre sauvegardé pour ${currentPlanifierJour} !\n\n ${fichiersOrdre.length} fichiers ordonnés\n  Diffusion prévue le ${dateDiffusion} à ${heureDiffusion}\n\n Pour créer la playlist M3U, cliquez maintenant sur le bouton "Générer playlist" en bas de la page.`);
            closePlanifierModal();
        } else {
            alert(' Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert(' Erreur lors de la sauvegarde');
    }
}

document.getElementById('detailsModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

async function showPlanning() {
    const modal = document.getElementById('detailsModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalDescription = document.getElementById('modalDescription');
    const mp3List = document.getElementById('mp3List');
    
    modalTitle.textContent = 'Statistiques de la semaine';
    modalDescription.textContent = 'Chargement...';
    mp3List.innerHTML = '';
    modal.classList.add('active');

    try {
        const response = await fetch(`${API_BASE}/marketing/stats/semaine`);
        const data = await response.json();

        if (data.success) {
            modalDescription.textContent = 'Aperçu des musiques par jour :';
            
            const jours = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE'];
            const couleurs = ['blue', 'indigo', 'purple', 'pink', 'rose', 'orange', 'green'];
            
            mp3List.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    ${jours.map((jour, idx) => {
                        const stats = data.data.par_jour[jour];
                        return `
                            <div onclick="showDetails('${jour}')" class="bg-gradient-to-br from-${couleurs[idx]}-50 to-${couleurs[idx]}-100 rounded-2xl p-6 border-2 border-${couleurs[idx]}-200 hover:border-${couleurs[idx]}-400 transition-all hover:shadow-xl cursor-pointer transform hover:scale-105">
                                <div class="flex items-center justify-between mb-3">
                                    <h4 class="text-xl font-bold text-gray-900">${jour}</h4>
                                    <svg class="w-6 h-6 text-${couleurs[idx]}-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                    </svg>
                                </div>
                                <div class="space-y-2">
                                    <div class="flex items-center gap-2">
                                        <svg class="w-5 h-5 text-${couleurs[idx]}-600" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                                        </svg>
                                        <span class="text-${couleurs[idx]}-700 font-semibold">
                                            ${stats.nombre_musiques} musique${stats.nombre_musiques !== 1 ? 's' : ''}
                                        </span>
                                    </div>
                                    <div class="text-sm text-gray-600">
                                        Durée: ${Math.floor(stats.duree_totale / 60)}min
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div class="mt-6 bg-gradient-to-r from-teal-50 to-teal-100 rounded-2xl p-6 border-2 border-teal-200">
                    <h4 class="text-xl font-bold text-gray-900 mb-4">Total de la semaine</h4>
                    <div class="grid grid-cols-3 gap-4">
                        <div>
                            <div class="text-3xl font-bold text-teal-600">${data.data.totaux.nombre_musiques}</div>
                            <div class="text-sm text-gray-600">Musiques</div>
                        </div>
                        <div>
                            <div class="text-3xl font-bold text-teal-600">${Math.floor(data.data.totaux.duree_totale / 60)}</div>
                            <div class="text-sm text-gray-600">Minutes</div>
                        </div>
                        <div>
                            <div class="text-3xl font-bold text-teal-600">${(data.data.totaux.taille_totale / (1024 * 1024)).toFixed(1)}</div>
                            <div class="text-sm text-gray-600">MB</div>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erreur:', error);
        modalDescription.textContent = '';
        mp3List.innerHTML = '<p class="text-red-500">Erreur lors du chargement des statistiques</p>';
    }
}

async function generatePlaylist() {
    if (!confirm('Générer les playlists pour toute la semaine ?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/marketing/playlist/generate/week`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();

        if (data.success) {
            alert(`${data.count} playlist(s) générée(s) avec succès!`);
            showPlaylistsGenerated(data.data);
        } else {
            alert('Erreur lors de la génération: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la génération des playlists');
    }
}

function showPlaylistsGenerated(playlists) {
    const modal = document.getElementById('detailsModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalDescription = document.getElementById('modalDescription');
    const mp3List = document.getElementById('mp3List');
    
    modalTitle.textContent = 'Playlists générées';
    modalDescription.textContent = `${playlists.length} playlist(s) M3U créée(s) avec succès :`;
    
    mp3List.innerHTML = `
        <div class="space-y-4">
            ${playlists.map(playlist => {
                const dureeMin = Math.floor(playlist.duree_total / 60);
                return `
                    <div class="bg-gradient-to-r from-teal-50 to-teal-100 rounded-xl p-6 border-2 border-teal-200">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-4">
                                <div class="w-12 h-12 bg-teal-500 rounded-xl flex items-center justify-center">
                                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
                                    </svg>
                                </div>
                                <div>
                                    <h4 class="text-lg font-bold text-gray-900">${playlist.nom_playlist}</h4>
                                    <p class="text-sm text-gray-600">Durée: ${dureeMin} minutes</p>
                                </div>
                            </div>
                            <a href="${API_BASE}/api/v1/playlist/download/${playlist.id_playlist}" class="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white font-semibold rounded-lg transition-colors">
                                Télécharger M3U
                            </a>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
        <div class="mt-6 text-center">
            <p class="text-gray-600 mb-4">Les fichiers M3U sont prêts à être déployés sur les lecteurs</p>
            <button onclick="closeModal()" class="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white font-semibold rounded-xl transition-colors">
                Fermer
            </button>
        </div>
    `;
    
    modal.classList.add('active');
}


document.getElementById('uploadModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeUploadModal();
    }
});

document.getElementById('planifierModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closePlanifierModal();
    }
});
