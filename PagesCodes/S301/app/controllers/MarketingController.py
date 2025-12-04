from flask import render_template, redirect, url_for, request
from app import app
from app.controllers.LoginController import reqlogged, reqrole
from app.services.UserService import UserService

us = UserService()

class MarketingController:

    @app.route('/marketing', methods = ['GET'])
    @reqrole("marketing")
    def marketing():
        metadata = {"title":"MarketingPage", "pagename": "marketing"}
        return render_template('marketing.html', metadata = metadata)