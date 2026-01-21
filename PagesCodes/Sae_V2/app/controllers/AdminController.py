from flask import render_template, redirect, url_for, request, jsonify
from app.services.AdminService import AdminService 
from app.controllers.LoginController import reqrole
from app import app
from app.models.BDDao import DatabaseInit
from app.services.UserService import UserService
from app.models.logDAO import logDAO
from datetime import datetime

ass = AdminService()
lgd = logDAO()
us = UserService()



@app.route("/admin")
@reqrole("ADMIN")
def admin_page():
    metadata = {"title" : " Admin Panel"}
    ass.findPlayer()
    ass.findStatut()
    print("hello")

    players = ass.getAllPlayerWithTheirLocalisation() 
    up = ass.getAllUp()
    groupes = us.getAllGroupes()
    users = us.getAllUsers()
    down = ass.getAllDown()
        
    return render_template('admin.html', 
                        groupes=groupes, 
                        users=users,
                        metadata=metadata,
                        devices=players,
                        up_devices=up,
                        down_devices=down)

@app.route("/get-devices")
@reqrole("ADMIN")
def send_devices_to_js():
    
    devices = ass.getAllPlayerWithTheirLocalisation()
    return jsonify([
        {"adresse_ip": d['adresse_ip'], "ville": d['ville'], "statut": d['statut']} 
        for d in devices
    ])


# ======================== GESTION UTILISATEURS ======================== #

@app.route("/signin", methods=['POST'])
@reqrole("ADMIN")
def signin():
    """Créer un nouvel utilisateur"""
    try:
        
        prenom = request.form['prenom'] 
        nom = request.form['nom'] 
        email = request.form['email']
        password = request.form['mot_de_passe']
        role = request.form["id_groupe"]
        
        
        print(f" Données reçues:")
        print(f"   Prénom: {prenom}")
        print(f"   Nom: {nom}")
        print(f"   Email: {email}")
        print(f"   Role: {role}")
        
        # validation
        if not all([prenom, nom, email, password, role]):
            missing = []
            if not prenom: missing.append("prénom")
            if not nom: missing.append("nom")
            if not email: missing.append("email")
            if not password: missing.append("mot de passe")
            if not role: missing.append("rôle")
            
            print(f" Champs manquants: {', '.join(missing)}")
            return jsonify({
                "success": False,
                "message": f"Champs manquants: {', '.join(missing)}"
            }), 400
        
    
        result = us.signin(prenom, nom, email, password, int(role))
        
        if result:
            print(f" Utilisateur {prenom} {nom} créé avec succès")
            return redirect(url_for('admin_page'))
        else:
            print(f" Échec création utilisateur")
            return jsonify({
                "success": False,
                "message": "Email déjà utilisé ou erreur lors de la création"
            }), 400
            
    except Exception as e:
        print(f" Erreur lors de l'ajout: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/admin/user/delete", methods=['POST'])
@reqrole("ADMIN")
def delete_user():
    """Supprimer un utilisateur"""
    try:
        email = request.form.get('email')
        
        if not email:
            return jsonify({
                "success": False,
                "message": "Email requis"
            }), 400
        
        result = us.deleteUser(email)
        
        if result.get('success'):
            return redirect(url_for('admin_page'))
        else:
            return jsonify(result), 403
            
    except Exception as e:
        print(f" Erreur lors de la suppression: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ================== Synchronisations des lecteurs =====================#
@app.route("/sync-all-devices", methods=['POST'])
@reqrole("ADMIN")
def sync_all_players():
    
    print("Je synchronise tout les lecteurs KO")
    ass.SyncAll()
    
    return jsonify({
        "status": "success",
        "message": "Tout a été bien synchroniser"        
    })
    

@app.route("/sync-device", methods=['POST'])
@reqrole("ADMIN")
def sync_player():
    data = request.json
    device_ip = data.get('ip')
    ass.Sync(device_ip)
    
    return jsonify({
        "status": "success", 
        "message": f"Appareil {device_ip} synchronisé",
    })

    
@app.route("/sync-selected-devices", methods=['POST'])
@reqrole("ADMIN")
def sync_selected_players():
    data = request.json
    selected = data.get('selected', [])
    
    for device in selected:
        ass.Sync(device['ip']) # let's goooo     
    
    return jsonify({
        "status": "success", 
        "message": f"les données {data} synchronisé",
    })
    
# ================ LOGS ================#

@app.route("/get-logs", methods=['POST'])
@reqrole("ADMIN")
def load_logs():
    data = request.json
    print(data)
    dateDebut = datetime.strptime(data['dates'][0], "%Y-%m-%d")
    dateFin = datetime.strptime(data['dates'][1], "%Y-%m-%d") 
    
    if(dateDebut > dateFin):
        return jsonify({
            "status": "failure",
            "message": "La date de debut ne doit pas être supérieur a la date de fin"
        })

    print(dateDebut)
    print(dateFin)
        
    lgd.WriteLog(dateDebut, dateFin) 
    return jsonify({
        "status": "success",
        "message": f"j'ai bien reçu les logs merci les dates sont {data}"
    })


# ======================== API POUR TESTER ADMIN ===================== #

@app.route("/api/v1/admin/view")
@reqrole("ADMIN")
def PlayersView():
    try:
        players = ass.getAllPlayer()
        playdict = {"status": True, "data": players}
        return jsonify(playdict)                     
    except Exception as e:
        return jsonify({"status": False, "Erreur": str(e)})             


@app.route("/api/v1/admin/view/down")
@reqrole("ADMIN")
def DownPlayersView():
    try:
        downed = ass.getAllDown()
        downed_dict = {"status": True, "data": downed}
        return jsonify(downed_dict)
    except Exception as e:
        return jsonify({"status": False, "Erreur": str(e)})    


@app.route("/api/v1/admin/view/Up")
@reqrole("ADMIN")
def UpPlayersView():
    try:
        Upped = ass.getAllUp()
        Upped_dict = {"status": True, "data": Upped}
        return jsonify(Upped_dict)
    except Exception as e:
        return jsonify({"status": False, "Erreur": str(e)})

    
@app.route("/api/v1/admin/view/<string:ip>")
@reqrole("ADMIN")
def ViewLecteurStatus(ip: str):
    
    try: 
        lect = ass.findByIP(ip)
        lect_name = lect.nom_lecteur
        lect_ip = lect.adresse_ip
        status = lect.statut
        return jsonify({"status": True, "lecteur_nom": lect_name, "IP": lect_ip, "lecteur Status": status})
    except Exception as e:
        return jsonify({"status": False, "Erreur": str(e)})
