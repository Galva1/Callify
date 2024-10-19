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
    g.matricula = session.get('matricula')
    g.cargo = session.get('cargo')
    g.idUsuario = session.get('idUsuario')

@app.context_processor
def inject_user():
    return dict(matricula=g.matricula, cargo=g.cargo, idUsuario=g.idUsuario)

def requer_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'matricula' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    cursor = conn.cursor()
    cursor.execute("SELECT idStatus, nm_status FROM Status")
    status_options = cursor.fetchall()  # Recupera todos os status
    print(status_options[0])
    return render_template('index.html', status_options=status_options)

@app.route('/quemSomos/')
def quemSomos():
    return render_template('quemSomos.html')

@app.route('/contatos/')
def contatos():
    return render_template('contatos.html')

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if 'matricula' in session:
        return redirect(url_for('menu')) 
    
    if request.method == 'POST':
        username = request.form['matricula']
        password = request.form['password']

        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash, cargo, matricula, idUsuario, ativo FROM Usuario WHERE matricula = ?",(username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[0], password) and user[4] == 1:
            session['cargo'] = user[1]
            session['matricula'] = user[2]
            session['idUsuario'] = user[3]
            return redirect(url_for('menu'))
        else:
            flash('Usuario ou senha invalidos!', 'danger')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/cadastro/')
def cadastro():
    return render_template('cadastro.html')

@app.route('/novoChamado/')
@requer_login
def novoChamado():
    return render_template('novoChamado.html')

@app.route('/menu/', methods=['GET'])
@requer_login
def menu():
    # Obter os dados de matricula e cargo da sessão
    idUsuario = session.get('idUsuario')
    usuario = session.get('matricula')
    cargo = session.get('cargo')

    cursor = conn.cursor()

    cursor.execute("SELECT idStatus, nm_status FROM Status")
    status_options = cursor.fetchall()

    query = """
        SELECT idChamado, titulo, descricao, Chamados.idStatus, observacao, 
               Chamados.idUrgencia, matriculaResponsavel, idOperador, 
               CONVERT(DATE, Chamados.dt_criacao), 
               CONVERT(DATE, dt_finalizado), u1.nm_usuario, 
               nm_urgencia, u2.nm_usuario, Status.nm_status 
        FROM Chamados 
        LEFT JOIN Usuario u1 ON u1.idUsuario = Chamados.idOperador 
        LEFT JOIN Status ON Status.idStatus = Chamados.idStatus 
        LEFT JOIN Urgencia ON Urgencia.idUrgencia = Chamados.idUrgencia 
        LEFT JOIN Usuario u2 ON u2.matricula = Chamados.matriculaResponsavel
        WHERE 1=1
    """

    parametros = []

    if cargo == 'usuario': 
        query += 'AND matriculaResponsavel = ?'
        parametros.append(usuario)

    elif cargo == 'operador':
        query += 'AND (Chamados.idOperador = ?) or (Chamados.idStatus = 1 and Chamados.idOperador is null)'
        parametros.append(idUsuario)


    cursor.execute(query, parametros)

    data = cursor.fetchall()

    novos = [chamado for chamado in data if chamado[3] == 1]
    fazendo = [chamado for chamado in data if chamado[3] == 2]
    finalizado = [chamado for chamado in data if chamado[3] in (3,4)]

    return render_template('menu.html',usuario=usuario, cargo=cargo, qt_chamados=len(data), campos=data, status_options=status_options, novos=novos, fazendo=fazendo, finalizado=finalizado)

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
            return jsonify({"message": f"Erro ao cadastrar usuario: {str(e)}"}), 500
        
        finally:
            cursor.close()
            return jsonify({"status": "sucess", "message":  "Usuário cadastrado com sucesso!"}), 201
            
    return(render_template('novoChamado.html'))

@app.route('/excluir', methods=['POST'])
def excluir_usuario():
    data = request.get_json()
    matricula = data.get('matricula')

    if not matricula:
        return jsonify({"message": "A matricula eh obrigatoria para excluir o usuario!"}), 400
    
    cursor = conn.cursor()
    cursor.execute("SELECT ativo FROM Usuario WHERE matricula = ?", matricula)
    ativo = cursor.fetchall()

    if ativo:
        return jsonify({"message": f"Usuario ja desativado!"}), 500
    
    try:
        cursor.execute("UPDATE Usuario SET ativo = 0 WHERE matricula = ?", matricula)
        conn.commit()
        return jsonify({"message": "Usuario desativado com sucesso!"}), 200
    except pyodbc.Error as e:
        return jsonify({"message": f"Erro ao desativar usuario: {str(e)}"}), 500
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

        if ((not titulo.strip()) or (not descricao.strip())):
                return jsonify({"message": "É necessário preencher titulo e descrição."}), 500
        
        if (chamado == 'nao'):
            if not(matricula):
                return jsonify({"message": "É necessário preencher a matricula do requerente."}), 500
        
        if not(matricula):
            matricula = session.get('matricula')

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

@app.route('/buscar', methods=['GET'])
def buscar():
    operador = request.args.get('operador')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    situacao = request.args.get('situacao')
    protocolo = request.args.get('protocolo')
    cursor = conn.cursor()

    # Obter as opções de situação
    cursor.execute("SELECT idStatus, nm_status FROM Status")
    status_options = cursor.fetchall()  

    # Consulta principal
    query = """
        SELECT idChamado, titulo, descricao, Chamados.idStatus, observacao, 
               Chamados.idUrgencia, matriculaResponsavel, idOperador, 
               CONVERT(DATE, Chamados.dt_criacao), 
               CONVERT(DATE, dt_finalizado), u1.nm_usuario, 
               nm_urgencia, u2.nm_usuario, Status.nm_status 
        FROM Chamados 
        LEFT JOIN Usuario u1 ON u1.idUsuario = Chamados.idOperador 
        LEFT JOIN Status ON Status.idStatus = Chamados.idStatus 
        LEFT JOIN Urgencia ON Urgencia.idUrgencia = Chamados.idUrgencia 
        LEFT JOIN Usuario u2 ON u2.matricula = Chamados.matriculaResponsavel
        WHERE 1=1
    """

    parametros = []

    if operador:
        query += 'AND u2.matricula = ?'
        parametros.append(operador)

    if start_date and end_date:
        query += " AND Chamados.dt_criacao BETWEEN ? AND ?"
        parametros.append(start_date)
        parametros.append(end_date)

    if situacao:
        query += " AND Status.idStatus = ?"
        parametros.append(situacao)

    if protocolo:
        query += " AND Chamados.idChamado = ?"
        parametros.append(protocolo)

    cursor.execute(query, parametros)
    data = cursor.fetchall()

    return render_template('menu.html', campos=data, status_options=status_options)


if __name__ == '__main__':
    app.run(debug= True)