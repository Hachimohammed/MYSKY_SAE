const API_BASE = window.location.origin;
let currentPlanifierJour = '';
let fichiersOrdre = [];
let draggedElement = null;

function showUploadModal(jour) {
    document.getElementById('uploadModalTitle').textContent = `Ajouter des musiques - ${jour}`;
    document.getElementById('jour_upload').value = jour;
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadProgress').style.display = 'none';
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

    document.getElementById('uploadProgress').style.display = 'block';
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
        document.getElementById('uploadProgress').style.display = 'none';
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
                <div onclick='showMp3Details(${JSON.stringify(fichier).replace(/'/g, "&apos;")})' class="fichier-card mb-3">
                    <div class="d-flex align-items-center justify-content-between gap-3">
                        <div class="d-flex align-items-center gap-3 flex-fill">
                            <div class="music-icon-container">
                                <svg width="20" height="20" fill="white" viewBox="0 0 20 20">
                                    <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                                </svg>
                            </div>
                            <div>
                                <h4 class="h6 fw-bold mb-0">${fichier.nom}</h4>
                                <p class="small text-muted mb-0">${fichier.artiste || 'Inconnu'}</p>
                            </div>
                        </div>
                        <svg width="20" height="20" fill="none" stroke="#a855f7" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                        </svg>
                    </div>
                </div>
            `).join('');
        } else {
            modalDescription.textContent = '';
            mp3List.innerHTML = '<p class="text-muted fst-italic">Aucune musique disponible pour ce jour</p>';
        }
    } catch (error) {
        console.error('Erreur:', error);
        modalDescription.textContent = '';
        mp3List.innerHTML = '<p class="text-danger">Erreur lors du chargement des données</p>';
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
        <div class="p-4 rounded-3" style="background: linear-gradient(to right, #f3e8ff, #ede9fe); border: 2px solid #e9d5ff;">
            <div class="d-flex align-items-start gap-4 mb-4">
                <div class="music-icon-lg flex-shrink-0">
                    <svg width="40" height="40" fill="white" viewBox="0 0 20 20">
                        <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                    </svg>
                </div>
                <div class="flex-fill">
                    <h4 class="h4 fw-bold mb-2">${fichier.nom}</h4>
                    <p class="mb-3 text-secondary">${fichier.artiste || 'Artiste inconnu'}</p>
                    <span class="badge" style="background: #e9d5ff; color: #6b21a8; font-size: 0.875rem; padding: 0.5rem 0.75rem;">
                        ${fichier.album || 'Album inconnu'}
                    </span>
                </div>
            </div>
            
            <div class="info-box">
                <div class="row g-3">
                    <div class="col-6">
                        <div class="text-muted small fw-medium mb-1">Type</div>
                        <div class="fw-bold h5 mb-0">${fichier.type_fichier.toUpperCase()}</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small fw-medium mb-1">Durée</div>
                        <div class="fw-bold h5 mb-0">${dureeMin}:${dureeSec.toString().padStart(2, '0')}</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small fw-medium mb-1">Taille</div>
                        <div class="fw-bold h5 mb-0">${tailleMB} MB</div>
                    </div>
                    <div class="col-6">
                        <div class="text-muted small fw-medium mb-1">Date d'ajout</div>
                        <div class="fw-bold h5 mb-0">${new Date(fichier.date_ajout).toLocaleDateString('fr-FR')}</div>
                    </div>
                </div>
            </div>
            
            <div class="d-flex gap-2 mt-4">
                <a href="${fichier.download_url}" class="btn btn-success flex-fill fw-bold">
                    Télécharger
                </a>
                <button onclick="confirmDeleteMp3(${fichier.id_fichier}, '${fichier.nom}')" class="btn btn-danger fw-bold">
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
        container.innerHTML = '<p class="text-muted fst-italic text-center py-4">Aucun fichier disponible</p>';
        return;
    }
    
    container.innerHTML = fichiersOrdre.map((fichier, index) => `
        <div 
            class="fichier-item fichier-card mb-3"
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
            <div class="d-flex align-items-center gap-3">
                <div class="flex-shrink-0">
                    <div class="d-flex align-items-center justify-content-center" style="width: 48px; height: 48px; background: #a855f7; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <span class="text-white h5 fw-bold mb-0">${index + 1}</span>
                    </div>
                </div>
                
                <div class="flex-shrink-0" style="color: #c084fc;">
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
                    </svg>
                </div>
                
                <div class="flex-fill">
                    <h4 class="h6 fw-bold mb-0">${fichier.nom}</h4>
                    <p class="small text-muted mb-0">${fichier.artiste} • ${fichier.duree_formattee}</p>
                </div>
                
                <div class="d-flex gap-2">
                    <button 
                        onclick="moveUp(${index}); event.stopPropagation();" 
                        class="btn btn-primary btn-sm d-flex align-items-center justify-content-center"
                        style="width: 40px; height: 40px; border-radius: 8px;"
                        ${index === 0 ? 'disabled style="opacity: 0.3; cursor: not-allowed;"' : ''}
                    >
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                        </svg>
                    </button>
                    <button 
                        onclick="moveDown(${index}); event.stopPropagation();" 
                        class="btn btn-primary btn-sm d-flex align-items-center justify-content-center"
                        style="width: 40px; height: 40px; border-radius: 8px;"
                        ${index === fichiersOrdre.length - 1 ? 'disabled style="opacity: 0.3; cursor: not-allowed;"' : ''}
                    >
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    
    if (!confirm(` Sauvegarder l'ordre de lecture pour ${currentPlanifierJour} ?\n\n${fichiersOrdre.length} fichiers seront ordonnés.\n Date de diffusion: ${dateDiffusion}\n Heure de diffusion: ${heureDiffusion}\n\nVous devrez ensuite cliquer sur "Générer playlist" pour créer les fichiers M3U.`)) {
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
            alert(` Ordre sauvegardé pour ${currentPlanifierJour} !\n\n ${fichiersOrdre.length} fichiers ordonnés\n Diffusion prévue le ${dateDiffusion} à ${heureDiffusion}\n\n Pour créer la playlist M3U, cliquez maintenant sur le bouton "Générer playlist" en bas de la page.`);
            closePlanifierModal();
        } else {
            alert(' Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert(' Erreur lors de la sauvegarde');
    }
}

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
            const couleurs = ['primary', 'info', 'purple', 'pink', 'danger', 'warning', 'success'];
            
            mp3List.innerHTML = `
                <div class="row g-3">
                    ${jours.map((jour, idx) => {
                        const stats = data.data.par_jour[jour] || { count: 0, duree_totale: 0 };
                        const nombreMusiques = stats.count || 0;
                        const dureeTotale = stats.duree_totale || 0;
                        
                        const bgColor = idx === 2 ? 'linear-gradient(135deg, #f3e8ff, #ede9fe)' : 
                                      idx === 3 ? 'linear-gradient(135deg, #fce7f3, #fbcfe8)' :
                                      `var(--bs-${couleurs[idx]}-bg-subtle)`;
                        return `
                            <div class="col-md-6">
                                <div onclick="showDetails('${jour}')" class="p-4 rounded-3 border-2 h-100" style="background: ${bgColor}; border: 2px solid var(--bs-${couleurs[idx]}-border-subtle); cursor: pointer; transition: all 0.3s;" onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 10px 15px -3px rgba(0,0,0,0.1)';" onmouseout="this.style.transform=''; this.style.boxShadow='';">
                                    <div class="d-flex align-items-center justify-content-between mb-3">
                                        <h4 class="h5 fw-bold mb-0">${jour}</h4>
                                        <svg width="24" height="24" fill="none" stroke="var(--bs-${couleurs[idx]})" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                                        </svg>
                                    </div>
                                    <div class="d-flex flex-column gap-2">
                                        <div class="d-flex align-items-center gap-2">
                                            <svg width="20" height="20" fill="var(--bs-${couleurs[idx]})" viewBox="0 0 20 20">
                                                <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                                            </svg>
                                            <span class="fw-semibold">${nombreMusiques} musique${nombreMusiques !== 1 ? 's' : ''}</span>
                                        </div>
                                        <div class="small text-muted">Durée: ${Math.floor(dureeTotale / 60)}min</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div class="mt-4 p-4 rounded-3" style="background: linear-gradient(to right, #f0fdfa, #ccfbf1); border: 2px solid #99f6e4;">
                    <h4 class="h5 fw-bold mb-3">Total de la semaine</h4>
                    <div class="row g-3">
                        <div class="col-4">
                            <div class="display-6 fw-bold text-primary">${data.data.totaux.nombre_musiques || 0}</div>
                            <div class="small text-muted">Musiques</div>
                        </div>
                        <div class="col-4">
                            <div class="display-6 fw-bold text-primary">${Math.floor((data.data.totaux.duree_totale || 0) / 60)}</div>
                            <div class="small text-muted">Minutes</div>
                        </div>
                        <div class="col-4">
                            <div class="display-6 fw-bold text-primary">${((data.data.totaux.taille_totale || 0) / (1024 * 1024)).toFixed(1)}</div>
                            <div class="small text-muted">MB</div>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erreur:', error);
        modalDescription.textContent = '';
        mp3List.innerHTML = '<p class="text-danger">Erreur lors du chargement des statistiques</p>';
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
        <div class="d-flex flex-column gap-3">
            ${playlists.map(playlist => {
                const dureeMin = Math.floor(playlist.duree_total / 60);
                return `
                    <div class="p-4 rounded-3" style="background: linear-gradient(to right, #f0fdfa, #ccfbf1); border: 2px solid #99f6e4;">
                        <div class="d-flex align-items-center justify-content-between">
                            <div class="d-flex align-items-center gap-3">
                                <div class="d-flex align-items-center justify-content-center" style="width: 48px; height: 48px; background: #14b8a6; border-radius: 12px;">
                                    <svg width="24" height="24" fill="none" stroke="white" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"/>
                                    </svg>
                                </div>
                                <div>
                                    <h4 class="h6 fw-bold mb-0">${playlist.nom_playlist}</h4>
                                    <p class="small text-muted mb-0">Durée: ${dureeMin} minutes</p>
                                </div>
                            </div>
                            <a href="${API_BASE}/api/v1/playlist/download/${playlist.id_playlist}" class="btn btn-success">
                                Télécharger M3U
                            </a>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
        <div class="mt-4 text-center">
            <p class="text-muted mb-3">Les fichiers M3U sont prêts à être déployés sur les lecteurs</p>
            <button onclick="closeModal()" class="btn btn-secondary">Fermer</button>
        </div>
    `;
    
    modal.classList.add('active');
}


document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('detailsModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });

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
});