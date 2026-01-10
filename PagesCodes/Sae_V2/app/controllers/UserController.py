from flask import Flask, request, redirect, url_for, render_template, session
from app import app
from app.models.UserDAO import UserSqliteDAO as UserDAO
from app.models.BDDao import DatabaseInit as BDDao

@app.route('/add_user', methods=['POST'])
def addUser():
    nom = request.form['firstname']
    prenom = request.form['name']
    email = request.form['email']
    mdp = BDDao._generatePwdHash(request.form['password'])
    id_Groupe = int(request.form['role'])

    UserDAO.addUser(prenom, nom, email, mdp, id_Groupe)

    return redirect(url_for('admin'))

@app.route('/admin')
def admin_page():
    groupes = UserDAO.getGroupes()
    return render_template('admin.html', groupes=groupes)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def deleteUser(user_id):

    if user_id == session['user_id']:
        return redirect(url_for('admin_page'))
    #empecher admin de se supprimer lui meme

    UserDAO.deleteUser(user_id)
    return redirect(url_for('admin'))

