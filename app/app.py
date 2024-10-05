from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
import pyodbc
import config
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = config.SECRET_KEY

conn = pyodbc.connect
(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-KVTDUEN\\SQLEXPRESS;'
    'DATABASE=ProjetoAcademico;'
    'Trusted_Connection=yes;'
)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/quemSomos/')
def quemSomos():
    return render_template('quemSomos.html')

@app.route('/contatos/')
def contatos():
    return render_template('contatos.html')

@app.route("/login/")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash FROM Usuario WHERE nm_usuario = ?",(username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[0], password):
            flash('Login bem-sucedido!','success')
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
        
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/home')
def home():
    return 'Bem vindo a página inicial!'

if __name__ == '__main__':
    app.run(debug= True)