from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
import pyodbc
import config
import os
from models import Usuario

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = config.SECRET_KEY

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-KVTDUEI\SQLEXPRESS;'
    'DATABASE=Callify;'
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

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash, cargo FROM Usuario WHERE nm_usuario = ?",(username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[0], password):
            session['user_id'] = username
            session['cargo'] = user[1]
            flash('Login bem-sucedido!','success')
            return redirect(url_for('menu'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
        
    return render_template('login.html')

@app.route('/cadastro/')
def cadastro():
    return render_template('cadastro.html')

@app.route('/menu/')
def menu():
    usuario = session.get('user_id')
    cargo = session.get('cargo')
    return render_template('menu.html',usuario=usuario, cargo=cargo)

@app.route('/cadastroUsuario/')
def cadastroUsuario():
    return render_template('cadastroUsuario.html')


@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()
    matricula = data.get('matricula')
    nome = data.get('nome')
    senha = data.get('senha')
    cargo = data.get('cargo')

    if not(matricula, nome, senha, cargo):
        return jsonify({"message":  "Todos os campos sao obrigatorios!"}),400

    hashed_password = generate_password_hash(senha)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Usuario (matricula, nm_usuario, senha_hash, cargo, dt_criacao, ativo) VALUES (?,?,?,?, GETDATE(), 1)", matricula, nome, hashed_password, cargo
        )
        conn.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201
    except pyodbc.Error as e:
        return jsonify({"message": f"Erro ao cadastrar usuário: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/excluir', methods=['POST'])
def excluir_usuario():
    data = request.get_json()
    matricula = data.get('matricula')

    if not matricula:
        return jsonify({"message": "A matrícula é obrigatória para excluir o usuário!"}), 400

    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Usuario SET ativo = 0 WHERE matricula = ?", matricula)
        conn.commit()
        return jsonify({"message": "Usuário desativado com sucesso!"}), 200
    except pyodbc.Error as e:
        return jsonify({"message": f"Erro ao desativar usuário: {str(e)}"}), 500
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug= True)