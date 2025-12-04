from flask import render_template, redirect, url_for, request
from app import app
from app.controllers.LoginController import reqlogged, reqrole
from app.services.UserService import UserService

us = UserService()

class AdminController:

    @app.route('/admin', methods = ['GET'])
    @reqrole("admin")
    def admin():
        metadata = {"title":"AdminPage", "pagename": "admin"}
        users = us.getUsers()
        return render_template('admin.html', metadata = metadata, data = users)