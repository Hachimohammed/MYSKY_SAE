let selectedFile = null;

// ===== CHARGEMENT INITIAL =====
window.addEventListener('DOMContentLoaded', () => {
    console.log(' Page commerciale chargée');
    
    // Rafraîchir la page toutes les 10 minutes pour mettre à jour les infos
    setInterval(() => {
        console.log(' Rafraîchissement automatique de la page');
        window.location.reload();
    }, 600000); 
});

// ===== SÉLECTION DE FICHIER =====
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type === 'audio/mpeg') {
        selectedFile = file;
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('filePreview').classList.remove('d-none');
        console.log(' Fichier sélectionné:', file.name);
    } else {
        alert(' Veuillez sélectionner un fichier MP3 valide');
        selectedFile = null;
    }
}

// ===== UPLOAD DE LA PUBLICITÉ =====
async function uploadPublicite() {
    if (!selectedFile) {
        alert(' Veuillez d\'abord sélectionner un fichier MP3');
        return;
    }
    
    console.log(' Upload en cours de:', selectedFile.name);
    
    const formData = new FormData();
    formData.append('filename', selectedFile);
    
    try {
        const response = await fetch('/commercial/upload-ad', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log(' Upload réussi:', data);
            
            // Afficher le modal d'attente
            document.getElementById('waitingFileName').textContent = selectedFile.name;
            document.getElementById('waitingDuration').textContent = formatTime(data.duration || 45);
            document.getElementById('waitingModal').classList.add('active');
            
            // Réinitialiser l'upload
            resetUpload();
            
        } else {
            console.error(' Erreur upload:', data.error);
            alert(' Erreur : ' + (data.error || 'Impossible de téléverser la publicité'));
        }
        
    } catch (error) {
        console.error(' Erreur connexion:', error);
        alert(' Erreur de connexion au serveur');
    }
}

// ===== FERMER LE MODAL ET RAFRAÎCHIR =====
function closeWaitingModal() {
    console.log(' Fermeture du modal et rafraîchissement');
    document.getElementById('waitingModal').classList.remove('active');
    // Rafraîchir la page pour voir la nouvelle pub dans l'historique
    window.location.reload();
}

// ===== RÉINITIALISER L'UPLOAD =====
function resetUpload() {
    document.getElementById('filePreview').classList.add('d-none');
    document.getElementById('fileInput').value = '';
    selectedFile = null;
    console.log('🧹 Formulaire réinitialisé');
}

// ===== FORMATER LE TEMPS =====
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`; 
}

// ===== FERMER LE MODAL EN CLIQUANT À L'EXTÉRIEUR =====
window.addEventListener('click', function(e) {
    const modal = document.getElementById('waitingModal');
    if (e.target === modal) {
        closeWaitingModal();
    }
});