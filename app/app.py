from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from werkzeug.security import check_password_hash, generate_password_hash
import pyodbc
import config
import os
from functools import wraps 
from models import Usuario

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = config.SECRET_KEY

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-KVTDUEI\SQLEXPRESS;'
    'DATABASE=Callify;'
    'Trusted_Connection=yes;'
)

@app.before_request
def load_user():
    g.user_id = session.get('user_id')
    g.cargo = session.get('cargo')

@app.context_processor
def inject_user():
    return dict(user_id=g.user_id, cargo=g.cargo)

def requer_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
    if 'user_id' in session:
        return redirect(url_for('menu')) 
    
    if request.method == 'POST':
        username = request.form['matricula']
        password = request.form['password']

        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash, cargo, matricula FROM Usuario WHERE matricula = ?",(username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[0], password):
            session['cargo'] = user[1]
            session['user_id'] = user[2]
            flash('Login bem-sucedido!','success')
            return redirect(url_for('menu'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/cadastro/')
@requer_login
def cadastro():
    return render_template('cadastro.html')

@app.route('/novoChamado/')
@requer_login
def novoChamado():
    return render_template('novoChamado.html')

@app.route('/menu/')
@requer_login
def menu():
    usuario = session.get('user_id')
    cargo = session.get('cargo')
    return render_template('menu.html',usuario=usuario, cargo=cargo)

@app.route('/cadastroUsuario/')
@requer_login
def cadastroUsuario():
    return render_template('cadastroUsuario.html')


@app.route('/cadastrar', methods=['POST'])
@requer_login
def cadastrar_usuario():

    if request.method == 'POST':
        data = request.get_json()
        matricula = data.get('matricula')
        nome = data.get('nome')
        senha = data.get('senha')
        cargo = data.get('cargo')

        if (not matricula.strip()) or (not nome.strip()) or (not senha.strip()) or (not cargo.strip()):
            return jsonify({"status": "error", "message":  "Todos os campos sao obrigatorios!"}),400
        
        hashed_password = generate_password_hash(senha)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Usuario (matricula, nm_usuario, senha_hash, cargo, dt_criacao, ativo) VALUES (?,?,?,?, GETDATE(), 1)", matricula, nome, hashed_password, cargo
            )
            conn.commit()
            
        except pyodbc.Error as e:
            return jsonify({"message": f"Erro ao cadastrar usuário: {str(e)}"}), 500
        
        finally:
            cursor.close()
            return jsonify({"status": "sucess", "message":  "Usuário cadastrado com sucesso!"}), 201
            
    return(render_template('novoChamado.html'))

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

@app.route('/cadastrarChamado', methods=['GET', 'POST'])
def cadastrar_chamado():
    if request.method == 'POST':
        data = request.get_json()
        titulo = data.get('titulo')
        descricao = data.get('descricao')
        matricula = data.get('matricula')
        chamado = data.get('chamado')

        if not(titulo, descricao):
                return jsonify({"message": "É necessário preencher titulo e descrição."})
        
        if (chamado == 'nao'):
            if not(matricula):
                return jsonify({"message": "É necessário preencher a matricula do requerente."})
        
        if not(matricula):
            matricula = session.get('user_id')

        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO Chamados (titulo, descricao, idStatus, observacao, idUrgencia, matriculaResponsavel, idOperador, dt_criacao, dt_finalizado) VALUES (?,?,1,null,2,?,null,GETDATE(),null)",titulo,descricao,matricula
            )
            conn.commit()
            return jsonify({"message": "Chamado cadastrado com sucesso!"}), 201
        
        except pyodbc.Error as e:
            return jsonify({"message": f"Erro ao cadastrar Chamado: {str(e)}"}), 500
        
        finally:
            cursor.close()        
    
    return render_template('novoChamado.html') 

if __name__ == '__main__':
    app.run(debug= True)