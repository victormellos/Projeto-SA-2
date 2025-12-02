from flask import render_template, request, redirect, session, flash
from app import app, get_db
import bcrypt
import sqlite3

def home():
    return redirect('/')

def fetchProducts():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM PRODUTOS ORDER BY preco ASC LIMIT 6")
    results = cursor.fetchall()
    
    return results

@app.route("/")
@app.route('/index')
def index():
    usuario = session.get("usuario")
    tipo = session.get("tipo")
    produtos = fetchProducts()
    return render_template('index.html', usuario_logado=usuario, tipo_usuario=tipo, produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log_nome = request.form.get("usuario")
        log_senha = request.form.get("senha")

        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT senha, nivel_de_acesso FROM funcionarios WHERE nome_funcionario=?", (log_nome,))
        row = cursor.fetchone()
        
        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[0]):
            session["usuario"] = log_nome
            session["tipo"] = "funcionario"
            session["cargo"] = row[1]
            flash('Login realizado com sucesso!', 'success')
            return redirect('/login')

        cursor.execute("SELECT senha FROM clientes WHERE nome_cliente=?", (log_nome,))
        row = cursor.fetchone()
        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[0]):
            session["usuario"] = log_nome
            session["tipo"] = "cliente"
            flash('Login realizado com sucesso!', 'success')
            return redirect('/login')

        flash('Usuário ou senha incorretos', 'error')
        return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin():
    if session.get("tipo") != "funcionario":
        return redirect('/login')

    usuario = session.get("usuario")

    conn = get_db()
    produtos = conn.execute(
        "SELECT id_produto, nome, preco, stock FROM produtos ORDER BY nome"
    ).fetchall()

    clientes = conn.execute(
        "SELECT id_cliente, nome_cliente, email, CPF FROM clientes ORDER BY nome_cliente"
    ).fetchall()

    return render_template(
        'admin.html',
        usuario_logado=usuario,
        produtos=produtos,
        clientes=clientes
    )


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        celular = request.form.get("celular")
        email = request.form.get("email")
        senha = request.form.get("senha")

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id_cliente FROM clientes WHERE CPF=?", (cpf,))
            if cursor.fetchone():
                flash('CPF já cadastrado no sistema!', 'error')
                return redirect('/cadastro')

            cursor.execute("SELECT id_cliente FROM clientes WHERE email=?", (email,))
            if cursor.fetchone():
                flash('E-mail já cadastrado no sistema!', 'error')
                return redirect('/cadastro')

            placa = request.form.get("placa")
            if placa:
                cursor.execute("SELECT id_veiculo FROM veiculos WHERE placa=?", (placa,))
                if cursor.fetchone():
                    flash('Placa já cadastrada no sistema!', 'error')
                    return redirect('/cadastro')

            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

            modelo = request.form.get("modelo")
            marca = request.form.get("marca")
            ano = request.form.get("ano")
            cor = request.form.get("cor")

            cursor.execute(
                "INSERT INTO clientes (nome_cliente, CPF, celular, email, senha) VALUES (?, ?, ?, ?, ?)",
                (nome, cpf, celular, email, senha_hash)
            )

            if placa and modelo and marca:
                cursor.execute(
                    "INSERT INTO veiculos (marca, cor, ano, modelo, placa) VALUES (?, ?, ?, ?, ?)",
                    (marca, cor, ano, modelo, placa)
                )

            conn.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect('/cadastro')

        except sqlite3.IntegrityError as e:
            conn.rollback()
            if 'CPF' in str(e):
                flash('CPF já cadastrado no sistema!', 'error')
            elif 'email' in str(e):
                flash('E-mail já cadastrado no sistema!', 'error')
            elif 'placa' in str(e):
                flash('Placa já cadastrada no sistema!', 'error')
            else:
                flash('Erro ao realizar cadastro. Verifique os dados informados.', 'error')
            return redirect('/cadastro')

        except Exception as e:
            conn.rollback()
            flash('Erro ao realizar cadastro. Tente novamente.', 'error')
            return redirect('/cadastro')

    return render_template('cadastro.html')