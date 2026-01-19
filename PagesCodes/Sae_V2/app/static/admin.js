document.addEventListener("DOMContentLoaded", function() {
// 3 premiers users affichés
    const rows = document.querySelectorAll('.user-row');
    const voirPlusBtn= document.getElementById('voirPlusBtn');

    if (rows.length > 3) {
        rows.forEach((row, index) => {
            if (index >= 3) row.style.display = 'none';
        });
    } else if (voirPlusBtn) {
        voirPlusBtn.style.display = 'none';
    }

    //si on appuie sur entrée après avoir tapé dans la barre de recherche, le filtre s'active
    document.getElementById('rechercheInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {filtreUsers();}
    });
});

// filtre par email
function filtreUsers() {
    const input = document.getElementById('rechercheInput');
    const filter = input.value.toLowerCase().trim();
    const rows = document.querySelectorAll('.user-row');
    const voirPlusBtn = document.getElementById('voirPlusBtn');

    // si la recherche est vide, on revient etat initial
    if (filter === "") {
        voirPlus(true); // Reset l'affichage à 3
        if (voirPlusBtn) voirPlusBtn.style.display = 'inline-block';
        return;
    }

    // recherche sur chaque ligne si la chaine de caractere recherche ets contenue dans l'adresse mail
    rows.forEach(row => {
        const emailCell = row.querySelector('.user-email-cell');
        if (emailCell) {
            // Correction : textContent sans parenthèses
            const emailText = (emailCell.textContent || emailCell.innerText).toLowerCase();

            if (emailText.includes(filter)) {
                row.style.display = ''; // Affiche si ça correspond
            } else {
                row.style.display = 'none'; // Cache sinon
            }
        }
    });

    // on cache "voir plus" si recherche active
    if (voirPlusBtn) {
        voirPlusBtn.style.display = 'none';
    }
}

// gérer le bouton "Voir plus" / "Voir moins"
let estAggrandi = false;

function voirPlus(forceReset = false) {
    const rows = document.querySelectorAll('.user-row');
    const btn = document.getElementById('voirPlusBtn');
    
    if (forceReset) {
        estAggrandi = false;
        btn.innerHTML = '<i class="bi bi-chevron-down"></i> Voir tous les utilisateurs';
        rows.forEach((row, index) => {
            if (index >= 3) row.style.display = 'none';
            else row.style.display = '';
        });
        return;
    }

    if (!estAggrandi) {
        // Afficher tout
        rows.forEach(row => row.style.display = '');
        btn.innerHTML = '<i class="bi bi-chevron-up"></i> Voir moins';
    } else {
        // Revenir à 3
        rows.forEach((row, index) => {
            if (index >= 3) row.style.display = 'none';
        });
        btn.innerHTML = '<i class="bi bi-chevron-down"></i> Voir tous les utilisateurs';
    }
    estAggrandi = !estAggrandi;
}

// FIN PARTIE USER

let devices = []

async function loadDevices() {
    const response = await fetch('/get-devices');
    const data = await response.json();
    
    devices = data.map(device => ({
        ip: device.adresse_ip,
        lieu: device.ville,
        statut: device.statut,
        fichier: 'Aucun',
        selected: false 
    }));

}
loadDevices();

const fichiers = ['jazz_lounge.mp3', 'ambiance_matinale.mp3', 'soft_piano.mp3', 'lounge_mix.mp3', 'friday_energy.mp3'];

function addUser() {
    
    document.getElementById('addUserForm').submit();
}

console.log(devices)

function renderDevices() {
    const table = document.getElementById('deviceTable');
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filterStatus = document.getElementById('filterStatus').value;

    const filteredDevices = devices.filter(device => {
        const matchSearch = device.ip.toLowerCase().includes(searchTerm) || 
                            device.lieu.toLowerCase().includes(searchTerm);
        const matchStatus = filterStatus === 'all' || device.statut === filterStatus;
        return matchSearch && matchStatus;
    });

    table.innerHTML = filteredDevices.map((device, index) => {
        const realIndex = devices.indexOf(device);
        const statusHtml = device.statut === 'UP'
            ? `<span class="status-badge status-up">
                <i class="bi bi-check-circle-fill"></i>
                UP
                </span>`
            : `<span class="status-badge status-ko">
                <i class="bi bi-x-circle-fill"></i>
                K/O
                </span>`;

        const syncButton = device.statut === 'KO'
            ? `<button onclick="syncDevice(${realIndex})" class="sync-btn">Synchroniser</button>`
            : '';

        return `
            <tr>
                <td>
                    <input type="checkbox" ${device.selected ? 'checked' : ''} onchange="toggleDevice(${realIndex})" class="form-check-input">
                </td>
                <td class="fw-semibold">${device.ip}</td>
                <td>${device.lieu}</td>
                <td class="${device.statut === 'KO' ? 'fst-italic text-muted' : ''}">${device.fichier}</td>
                <td>${statusHtml}</td>
                <td>${syncButton}</td>
            </tr>
        `;
    }).join('');
}

function syncDevice(index) {
    const device = devices[index];
    console.log(device)
    const button = event.target;

    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    
    
    fetch('/sync-device', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: device.ip })
})
.then(response => response.json()).then(data => {

setTimeout(() => {
    if (data.status === 'success') {
        device.statut = 'UP';
        
        device.fichier = data.new_file || fichiers[Math.floor(Math.random() * fichiers.length)];
        
        
        renderDevices();
        if (typeof updateStats === "function") updateStats();
        
        console.log("Synchro réussie pour :", device.ip);
    } else {
        alert("Erreur Python : " + data.message);
        button.disabled = false;
        button.innerHTML = originalContent;
    }
}, 2000); 
})
.catch(error => {
console.error("Erreur réseau :", error);
button.disabled = false;
button.innerHTML = originalContent;
alert("Impossible de contacter le serveur Flask");
});
}

function syncAllKO() {
    const koDevices = devices.filter(d => d.statut === 'KO');
    if (!confirm(`Voulez-vous synchroniser les ${koDevices.length} appareils K/O ?`)) {
        return;
    }

    try{
        fetch('/sync-all-devices',{
        method :'POST',
        headers: { 'Content-Type': 'application/json' },
    })

        let koCount = 0;
        devices.forEach(device => {
        if (device.statut === 'KO') {
            koCount++;
            setTimeout(() => {
                device.statut = 'UP';
                device.fichier = fichiers[Math.floor(Math.random() * fichiers.length)];
                renderDevices();
                updateStats();
            }, koCount * 100);
        }
        
        
    });

}catch(error){
console.error("Erreur lors de la requête :", error);
alert("Impossible de contacter le serveur. La synchronisation n'a pas été effectuée.");

}  
}




function toggleDevice(index) {
    devices[index].selected = !devices[index].selected;
    updateSelectionUI();
}

function toggleSelectAll() {
    const checked = document.getElementById('selectAll').checked;
    devices.forEach(device => device.selected = checked);
    renderDevices();
    updateSelectionUI();
}

function updateSelectionUI() {
    const selectedCount = devices.filter(d => d.selected).length;
    document.getElementById('selectedCount').textContent = selectedCount;
    document.getElementById('bulkActions').classList.toggle('d-none', selectedCount === 0);
}

function syncSelected() {
    const selected = devices.filter(d => d.selected);
    if (selected.length === 0) return;
    
    try{
    fetch('/sync-selected-devices',{
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selected })
    } )

    

    selected.forEach((device, i) => {
        setTimeout(() => {
            device.status = 'UP';
            device.fichier = fichiers[Math.floor(Math.random() * fichiers.length)];
            device.selected = false;
            renderDevices();
            updateStats();
            updateSelectionUI();
        }, i * 100);
    });
}   catch(error){
    console.error("Erreur lors de la requête :", error);
    alert("Impossible de contacter le serveur. La synchronisation n'a pas été effectuée.");
    }
}


function clearSelection() {
    devices.forEach(d => d.selected = false);
    document.getElementById('selectAll').checked = false;
    renderDevices();
    updateSelectionUI();
}

function filterDevices() {
    renderDevices();
}

function updateStats() {
    const total = devices.length;
    const up = devices.filter(d => d.statut === 'UP').length;
    const ko = devices.filter(d => d.statut === 'KO').length;

    document.getElementById('totalDevices').textContent = total;
    document.getElementById('upDevices').textContent = up;
    document.getElementById('koDevices').textContent = ko;
}

async function exportHistory() {
    const dateDebut = document.getElementById('dateDebut').value;
    const dateFin = document.getElementById('dateFin').value;

    if (!dateDebut || !dateFin) {
        alert(' Veuillez sélectionner les deux dates');
        return;
    }

    try{

        const dates = [dateDebut,dateFin] 
    
        const response = await fetch("/get-logs",{
            method : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dates })
        })
        console.log(response)
        const rep_json  = await response.json()
        console.log(rep_json) 
        if(rep_json.status === "failure"){
            alert(" Date de début doit être inférieur a la date de fin");
            return;
        }
        
    /* let content = `═══════════════════════════════════════════════════════
MySky Audio - Historique des Appareils
Le ciel n'est plus une limite
═══════════════════════════════════════════════════════

Période: Du ${dateDebut} au ${dateFin}

Adresse IP       | Lieu                  | Fichier             | État
────────────────────────────────────────────────────────────────────
`;

    devices.slice(0, 50).forEach(device => {
        content += `${device.ip.padEnd(16)} | ${device.lieu.padEnd(21)} | ${device.fichier.padEnd(19)} | ${device.statut}\n`;
    });
    console.log(devices.length)

    if(devices.length > 50){ 
        content += `\n... et ${devices.length - 50} autres appareils\n\n`;
    }else{
        content +=  `\nc'est tout les appareils \n\n`;
    }    
    content += `═══════════════════════════════════════════════════════\n`;
    content += `Total: ${devices.length} appareils | UP: ${devices.filter(d => d.statut === 'UP').length} | K/O: ${devices.filter(d => d.statut === 'KO').length}\n`;
    content += `Généré le ${new Date().toLocaleString('fr-FR')}\n`;

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mysky_historique_${dateDebut}_${dateFin}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url); */

    } catch(error){
        console.log("Erreur : " + error)
        alert("Nous avons pas pu récuperer les logs")
    }
}

window.onload = function() {
    console.log("mon reuf?")
    renderDevices();
};