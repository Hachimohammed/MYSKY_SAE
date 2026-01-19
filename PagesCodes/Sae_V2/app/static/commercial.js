let isPlaying = true;
let selectedFile = null;
let currentVolume = 75;
let isMuted = false;
let volumeBeforeMute = 75;

// Simulation de progression de la musique
setInterval(() => {
    if (isPlaying) {
        const progressBar = document.getElementById('progressBar');
        const progressGlow = document.getElementById('progressGlow');
        let currentWidth = parseFloat(progressBar.style.width) || 45;
        currentWidth += 0.5;
        if (currentWidth >= 100) currentWidth = 0;
        progressBar.style.width = currentWidth + '%';
        progressGlow.style.width = currentWidth + '%';
        
        // Mise à jour du temps
        const totalSeconds = Math.floor((currentWidth / 100) * 300); // 5 min = 300 sec
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        document.getElementById('currentTime').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
}, 1000);

// Gestion du volume
function updateVolume(value) {
    currentVolume = value;
    document.getElementById('volumeValue').textContent = value + '%';
    
    // Mise à jour du gradient du slider
    const slider = document.getElementById('volumeSlider');
    slider.style.background = `linear-gradient(to right, rgb(168, 85, 247) 0%, rgb(236, 72, 153) ${value}%, rgb(71, 85, 105) ${value}%, rgb(71, 85, 105) 100%)`;
    
    // Changer l'icône selon le volume
    updateVolumeIcon(value);
}

function updateVolumeIcon(volume) {
    const icon = document.getElementById('volumeIcon');
    if (volume == 0) {
        icon.innerHTML = '<path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM12.293 7.293a1 1 0 011.414 0L15 8.586l1.293-1.293a1 1 0 111.414 1.414L16.414 10l1.293 1.293a1 1 0 01-1.414 1.414L15 11.414l-1.293 1.293a1 1 0 01-1.414-1.414L13.586 10l-1.293-1.293a1 1 0 010-1.414z" clip-rule="evenodd"/>';
    } else if (volume < 50) {
        icon.innerHTML = '<path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM12.293 7.293a1 1 0 011.414 0L15 8.586l1.293-1.293a1 1 0 111.414 1.414L16.414 10l1.293 1.293a1 1 0 01-1.414 1.414L15 11.414l-1.293 1.293a1 1 0 01-1.414-1.414L13.586 10l-1.293-1.293a1 1 0 010-1.414z" clip-rule="evenodd"/>';
    } else {
        icon.innerHTML = '<path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clip-rule="evenodd"/>';
    }
}

function toggleMute() {
    const slider = document.getElementById('volumeSlider');
    const muteBtn = document.getElementById('muteBtn');
    
    if (!isMuted) {
        // Mute
        volumeBeforeMute = currentVolume;
        updateVolume(0);
        slider.value = 0;
        muteBtn.classList.add('bg-red-600');
        muteBtn.classList.remove('bg-slate-700/50');
        isMuted = true;
    } else {
        // Unmute
        updateVolume(volumeBeforeMute);
        slider.value = volumeBeforeMute;
        muteBtn.classList.remove('bg-red-600');
        muteBtn.classList.add('bg-slate-700/50');
        isMuted = false;
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type === 'audio/mpeg') {
        selectedFile = file;
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('filePreview').classList.remove('hidden');
    } else {
        alert('⚠️ Veuillez sélectionner un fichier MP3 valide');
    }
}

function diffuserPublicite() {
    if (!selectedFile) return;
    
    // Arrêt automatique de la musique
    isPlaying = false;
    
    // Afficher la modal de diffusion
    document.getElementById('adFileName').textContent = selectedFile.name;
    document.getElementById('interruptModal').classList.add('active');
    
    // Simuler la progression de la pub
    let progress = 0;
    const adInterval = setInterval(() => {
        progress += 2;
        document.getElementById('adProgress').style.width = progress + '%';
        
        if (progress >= 100) {
            clearInterval(adInterval);
            setTimeout(() => {
                // Reprendre la musique automatiquement
                isPlaying = true;
                closeModal();
                
                // Ajouter à l'historique
                addToHistory(selectedFile.name);
                
                // Réinitialiser
                document.getElementById('filePreview').classList.add('hidden');
                document.getElementById('fileInput').value = '';
                selectedFile = null;
                
                alert('✅ Publicité diffusée avec succès!\n\n🎵 La musique a repris automatiquement sur tous les appareils.');
            }, 500);
        }
    }, 100);
}

function addToHistory(fileName) {
    const historyContainer = document.querySelector('.space-y-3');
    const newEntry = document.createElement('div');
    newEntry.className = 'flex items-center justify-between p-5 bg-orange-50 rounded-xl border-2 border-orange-200';
    newEntry.innerHTML = `
        <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"/>
                </svg>
            </div>
            <div>
                <p class="font-bold text-gray-900 text-lg">${fileName}</p>
                <p class="text-sm text-gray-600">Diffusée à l'instant</p>
            </div>
        </div>
        <div class="text-right">
            <span class="px-4 py-2 bg-green-100 text-green-700 font-bold rounded-lg text-sm">✓ Terminée</span>
            <p class="text-gray-600 text-sm mt-1">Durée: 0:45</p>
        </div>
    `;
    historyContainer.insertBefore(newEntry, historyContainer.firstChild);
}

function showInterruptModal() {
    document.getElementById('interruptModal').classList.add('active');
}

function closeModal() {
    document.getElementById('interruptModal').classList.remove('active');
    document.getElementById('adProgress').style.width = '0%';
}

function confirmInterrupt() {
    alert('⏸️ Playlist interrompue sur tous les appareils!\n\nVous pouvez maintenant téléverser votre publicité.');
    closeModal();
}

// Fermer la modal en cliquant en dehors
document.getElementById('interruptModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});