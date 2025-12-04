from flask import render_template, redirect, url_for, request
from app import app
from app.controllers.LoginController import reqlogged, reqrole
from app.services.UserService import UserService

us = UserService()

class CommercialController:

    @app.route('/commercial', methods = ['GET'])
    @reqrole("commercial")
    def marketing():
        metadata = {"title":"CommercialPage", "pagename": "commercial"}
        return render_template('commercial.html', metadata = metadata)