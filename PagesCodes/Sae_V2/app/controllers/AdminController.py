from flask import render_template, redirect, url_for, request ,jsonify
from app.services.AdminService import AdminService 
from app.controllers.LoginController import reqrole
from app import app
from app.models.BDDao import DatabaseInit



ass = AdminService()







@reqrole("ADMIN")
def page():
    metadata = {"title" : " Admin Panel"}
    players = ass.getAllPlayer()       
    
    
    return render_template('admin.html',metadata=metadata)





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
             
            
            
            
        