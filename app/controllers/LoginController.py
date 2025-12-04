from os import abort
from flask import render_template, redirect, url_for, request
# imports nécessaires pour la connexion
from flask import session, flash
from app import app
from functools import wraps

from app.services.UserService import UserService

def reqlogged(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged' in session:
			return f(*args, **kwargs)
		else:
			flash('Vous devez vous connecter.') # message flash
			return redirect(url_for('login'))
	return wrap

def reqrole(role):
	def wrap(f):
		@wraps(f)
		def verifyRole(*args, **kwargs):
			if 'logged' not in session:
				flash("Vous devez vous connecter.")
				return redirect(url_for('login'))
			else:
				if session['role']!=role:
					abort(403)
				else:
					return f(*args, **kwargs) 
		return verifyRole
	return wrap	

us = UserService()

class LoginController:

	@app.route('/login', methods=['GET', 'POST'])
	def login():
		msg_error = None
		if request.method == 'POST':
			user = us.login(request.form["username"], request.form["password"])
			if user:
				session["logged"] = True
				session["username"] = user.username
				session["role"] = user.role
				return redirect(url_for("index"))
			else:
				msg_error = 'Identifiant ou mot de passe incorrect'
		return render_template('login.html', msg_error=msg_error)
	
	@app.route("/signin", methods=['GET', 'POST'])
	def signin():
		if request.method == "POST":
			result = us.signin(request.form["username"], request.form["password"])
			if result:
				session["logged"] = True
				session["username"] = request.form["username"]
				session["role"] = "lecteur"
				return redirect(url_for('index'))
			else:
				return render_template("signin.html", msg_error="Creation de compte impossible")
		else:
			return render_template('signin.html', msg_error=None)
		
	@app.route('/logout')
	@reqlogged
	def logout():
		session.clear()
		flash('Vous vous êtes deconnectés')
		return redirect(url_for('login'))