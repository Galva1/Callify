import pyodbc

class Database:
    def __init__(self):
        self.connection_string = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=DESKTOP-KVTDUEI\SQLEXPRESS;'
            'DATABASE=Callify;'
            'Trusted_Connection=yes;'
            )
    
    def get_connection(self):
        return pyodbc.connect(self.connection_string)

class Usuario:
    def __init__(self, idusuario, matricula, nm_usuario, senha_hash):
        self.idusuario = idusuario
        self.matricula = matricula
        self.nm_usuario = nm_usuario
        self.senha_hash = senha_hash

    @classmethod
    def get_usuario_by_id(cls, user_id):
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuario WHERE idUsuario = ?",(user_id,))
        row = cursor.fetchone()
        conn.close()

        if row():
            return cls(row.idUsuario, row.matricula, row.nm_usuario, row.senha_hash)
        return None

    @classmethod
    def get_usuario_by_matricula(cls, matricula):
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuario WHERE matricula = ?", (matricula,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(row.idUsuario, row.matricula, row.nm_usuario, row.senha_hash)
        return None