from flask import render_template, redirect, url_for, request ,jsonify
from app.services.AdminService import AdminService 
from app.controllers.LoginController import reqrole
from app import app
from app.models.BDDao import DatabaseInit
from app.models.logDAO import logDAO
from datetime import datetime

ass = AdminService()
lgd = logDAO()





@app.route("/admin")
@reqrole("ADMIN")
def admin_page():
    metadata = {"title" : " Admin Panel"}
    print("hello")
    players = ass.getAllPlayerWithTheirLocalisation() 
    up = ass.getAllUp()
    down = ass.getAllDown()
        
    return render_template('admin.html',metadata=metadata,devices=players,up_devices=up,down_devices=down)


#================== Synchronisations des lecteurs =====================#
@app.route("/sync-all-devices",methods=['POST'])
@reqrole("ADMIN")
def sync_all_players():
    
    print("Je synchronise tout les lecteurs KO")
    ass.SyncAll()
    
    return jsonify({
        "status : " : "success",
        "message"  : " Tout a été bien synchroniser"        
    })
    

@app.route("/sync-device" , methods=['POST'])
@reqrole("ADMIN")
def sync_player():
    data = request.json
    device_ip = data.get('ip')
    
    print(f"est ce que j'ai reçu {device_ip} ? ")
    ass.Sync(device_ip)
    
    return jsonify({
        "status": "success", 
        "message": f"Appareil {device_ip} synchronisé",
    })

    
@app.route("/sync-selected-devices",methods=['POST'])
@reqrole("ADMIN")
def sync_selected_players():
    data = request.json
    selected = data.get('selected',[])
    
    for device in selected:
        print(device['ip'])
        ass.Sync(device['ip']) # let's goooo     
    
    return jsonify({
        "status": "success", 
        "message": f"les données {data} synchronisé",
    })
    
#================ LOGS ================#



@app.route("/get-logs",methods=['POST'])
@reqrole("ADMIN")
def load_logs():
    data = request.json
    print(data)
    dateDebut = datetime.strptime(data['dates'][0],"%Y-%m-%d")
    dateFin = datetime.strptime(data['dates'][1], "%Y-%m-%d") 
    
    if(dateDebut > dateFin):
        print("c'est un fail")
        return jsonify({
            "status" : "failure",
            "message" :"La date de debut ne doit pas être supérieur a la date de fin"
        })

    print(dateDebut)
    print(dateFin)
        
    lgd.WriteLog(dateDebut,dateFin) 
    return jsonify({
        "status" : "success",
        "message" :f"j'ai bien reçu les logs merci les dates sont {data}"
    })


# ======================== API POUR TESTER ADMIN ===================== #

@app.route("/api/v1/admin/view")
@reqrole("ADMIN")
def PlayersView():
    try:
        players = ass.getAllPlayer()
        playdict = {"status  " : True,"data  " : players}
        return jsonify(playdict)                     
    except Exception as e:
        return jsonify({"status " : False, "Erreur  " : str(e)})             


@app.route("/api/v1/admin/view/down")
@reqrole("ADMIN")
def DownPlayersView():
    try:
        downed = ass.getAllDown()
        downed_dict = {"status " : True, "data " : downed}
        return jsonify(downed_dict)
    except Exception as e:
        return jsonify({"status  " : False, "Erreur  " : str(e)})    


@app.route("/api/v1/admin/view/Up")
@reqrole("ADMIN")
def UpPlayersView():
    try:
        Upped =  ass.getAllUp()
        Upped_dict = {"status " : True , "data : " : Upped}
        return jsonify(Upped_dict)
    except Exception as e:
        return jsonify({"status " : False, "Erreur  " : str(e)})

    
@app.route("/api/v1/admin/view/<string:ip>")
@reqrole("ADMIN")
def ViewLecteurStatus(ip : str):
    
    try: 
        lect = ass.findByIP(ip)
        lect_name = lect.nom_lecteur
        lect_ip = lect.adresse_ip
        status = lect.statut
        return jsonify({"status "  : True , "lecteur_nom "  : lect_name , "IP ": lect_ip," lecteur Status  " : status})
    except Exception as e:
        return jsonify({"status : " : False , "Erreur :" : str(e)})
             
            
            
            
        