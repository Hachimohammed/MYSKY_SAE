from flask import render_template, redirect, url_for, request, session, abort, flash
from functools import wraps 
from app import app
from app.services.UserService import UserService
from app.models.UserDAO import UserSqliteDAO as UserDAO
from app.models.BDDao import DatabaseInit as BDDao

us = UserService()

def reqrole(*roles):
    def wrap(f):
        @wraps(f)
        def verifyRole(*args, **kwargs):
            if not session.get('logged'):
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                abort(403)
            return f(*args, **kwargs)
        return verifyRole
    return wrap

def reqlogged(f):
	@wraps(f) # permet de conserver le nom de la fonction, la nouvelle doc et les arguments
	def wrap(*args, **kwargs):
		if 'logged' in session:
			return f(*args, **kwargs)
		else:
			flash('Denied. You need to login.') # message flash
			return redirect(url_for('login'))
	return wrap

class LoginController:

    @app.route("/", methods=["GET", "POST"]) 
    def login(): 
        msg_error = None
        if request.method == 'POST':
            email = request.form["username"]
            pwd = request.form['password']
            user = us.login(email, pwd)

            if user:
                session["logged"] = True
                session['username'] = user.email
                session['role'] = user.nom_groupe

                if user.nom_groupe == "ADMIN":
                    return redirect(url_for("admin_page"))
                elif user.nom_groupe == "COMMERCIAL":
                    return redirect(url_for("commercial"))
                elif user.nom_groupe=="MARKETING":
                    return redirect(url_for("marketing"))
            else:
                msg_error = "Identifiants invalides."

        metadata = {"title": "MySky", "msg_error": msg_error}
        return render_template('login.html', metadata=metadata)

    @app.route("/logout")
    @reqlogged
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route('/commercial')
    @reqrole("ADMIN", "COMMERCIAL")
    def commercial():
        return render_template('commercial.html')

    @app.route('/marketing')
    @reqrole("ADMIN" , "MARKETING")
    def marketing():
        return redirect(url_for('marketing_dashboard'))
