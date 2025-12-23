from flask import render_template, redirect, url_for, request, session, abort
from functools import wraps 
from app import app
from app.services.UserService import UserService

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

@app.route("/", methods=["GET", "POST"]) 
def login(): 
    msg_error = None
    if request.method == 'POST':
        email = request.form.get('username')
        pwd = request.form.get('password')
        
        user = us.login(email, pwd)
        
        if user:
            session["logged"] = True
            session['username'] = user['email']
            session['role'] = user['role'] 
            
            
            if user['role'] == "ADMIN":
                return redirect(url_for("admin"))
            elif user['role'] == "COMMERCIAL":
                return redirect(url_for("commercial"))
            else:
                return redirect(url_for("marketing"))
        else:
            msg_error = "Identifiants invalides."

    metadata = {"title": "MySky", "msg_error": msg_error}
    return render_template('login.html', metadata=metadata)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin")
@reqrole("ADMIN")
def admin():
    return render_template('admin.html')

@app.route('/commercial')
@reqrole("ADMIN", "COMMERCIAL")
def commercial():
    return render_template('commercial.html')

@app.route('/marketing')
@reqrole("ADMIN" , "MARKETING")
def marketing():
    return render_template('marketing.html')