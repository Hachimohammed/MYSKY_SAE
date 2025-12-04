from flask import render_template, redirect, url_for, request
# imports nécessaires pour la connexion
from flask import session, flash
from flask import  abort
from app import app
from app.services.UserService import UserService
from app.controllers.LoginController import reqrole

us = UserService()

class UserController:

	@app.route('/user/delete', methods=['POST'])
	@reqrole("admin")
	def deleteUser():
		res = us.deleteUser(request.form["username"])
		return redirect(url_for("admin"))