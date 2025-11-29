from flask import render_template, request
from app import app, get_db
import bcrypt

import sqlite3


@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log_nome = request.form.get("usuario")
        log_senha = request.form.get("senha")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT senha FROM funcionarios WHERE nome_funcionario=?", (log_nome,))
        row = cursor.fetchone()

        if row:
            hash_senha = row[0]  
            if bcrypt.checkpw(log_senha.encode('utf-8'), hash_senha):
                conn.close()
                return "Login feito com sucesso"
            

        cursor.execute("SELECT senha FROM clientes WHERE nome_cliente=?", (log_nome,))
        row = cursor.fetchone()

        if row:
            hash_senha = row[0]  
            if bcrypt.checkpw(log_senha.encode('utf-8'), hash_senha):
                conn.close()
                return "Login feito com sucesso"




        conn.close()
        return "Usuário ou senha incorretos"

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':

        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        celular = request.form.get("celular")
        email = request.form.get("email")
        senha = request.form.get("senha")


        salt = bcrypt.gensalt()  # Gera um salt aleatório
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)

        conn = get_db()
        cursor = conn.cursor()

        tipo_usuario = request.form.get("tipo_usuario") 

        match tipo_usuario:
            case "cliente":
                placa = request.form.get("placa")
                modelo = request.form.get("modelo")
                marca = request.form.get("marca")
                ano = request.form.get("ano")
                cor = request.form.get("cor")

                cursor.execute("""
                INSERT INTO clientes (nome_cliente, CPF, celular, email, senha)
                VALUES (?, ?, ?, ?, ?)
                """, (nome, cpf, celular, email, senha_hash))

                cursor.execute("""
                INSERT INTO veiculos (marca, cor, ano, modelo, placa)
                VALUES (?, ?, ?, ?, ?)
                """, (marca, cor, ano, modelo, placa))
                
                conn.commit()
                conn.close()
                return "Cadastro do cliente feito com sucesso"

            case "funcionario":
                cargo = request.form.get("cargo")

                cursor.execute("""
                INSERT INTO funcionarios (nome_funcionario, nivel_de_acesso, senha)
                VALUES (?, ?, ?)
                """, (nome, cargo, senha_hash))
                conn.commit()
                conn.close()
                return "Cadastro do funcionario feito com sucesso"
                
    return render_template('cadastro.html')


# ← só essa linha abaixo
import routes.produto