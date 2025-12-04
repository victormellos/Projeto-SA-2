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
        
        cursor.execute("SELECT id_cliente, senha FROM clientes WHERE nome_cliente=?", (log_nome,))
        row = cursor.fetchone()

        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[1]):
            session["usuario"] = log_nome
            session["tipo"] = "cliente"
            session["id_cliente"] = row[0] # id
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

@app.route('/pedir', methods=['GET', 'POST'])
def pedir():
    if not session:
        return render_template('login.html')

    conn = get_db()
    cursor = conn.cursor()
    
    id_cliente = session.get("id_cliente")

    cursor.execute("SELECT * FROM CLIENTES WHERE id_cliente = ?" (id_cliente))    
    cliente = cursor.fetchone()
    return render_template('pedir.html', cliente=cliente)

@app.route("/pedir/troca-pecas", methods=["POST"])
def troca_pecas():

    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    email = request.form.get("email")
    marca = request.form.get("marca")
    modelo = request.form.get("modelo")
    ano = request.form.get("ano")
    placa = request.form.get("placa")
    pecas = request.form.get("pecas")
    descricao = request.form.get("descricao")
    observacoes = request.form.get("observacoes")

    print("\n📦 TROCA DE PEÇAS RECEBIDO:")
    print("Nome:", nome)
    print("Telefone:", telefone)
    print("Email:", email)
    print("Marca:", marca)
    print("Modelo:", modelo)
    print("Ano:", ano)
    print("Placa:", placa)
    print("Peças:", pecas)
    print("Descrição:", descricao)
    print("Observações:", observacoes)

    return "Recebido (Troca de Peças)"

@app.route("/pedir/emergencial", methods=["POST"])
def emergencial():

    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    email = request.form.get("email")
    marca = request.form.get("marca")
    modelo = request.form.get("modelo")
    ano = request.form.get("ano")
    placa = request.form.get("placa")
    urgencia = request.form.get("urgencia")
    localizacao = request.form.get("localizacao")
    problema = request.form.get("problema")
    pode_dirigir = request.form.get("pode_dirigir")
    observacoes = request.form.get("observacoes")

    print("\n🚨 EMERGENCIAL RECEBIDO:")
    print("Nome:", nome)
    print("Telefone:", telefone)
    print("Email:", email)
    print("Marca:", marca)
    print("Modelo:", modelo)
    print("Ano:", ano)
    print("Placa:", placa)
    print("Urgência:", urgencia)
    print("Localização:", localizacao)
    print("Problema:", problema)
    print("Pode dirigir:", pode_dirigir)
    print("Observações:", observacoes)

    return "Recebido (Emergencial)"

@app.route("/pedir/agendamento", methods=["POST"])
def agendamento():

    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    email = request.form.get("email")
    marca = request.form.get("marca")
    modelo = request.form.get("modelo")
    ano = request.form.get("ano")
    placa = request.form.get("placa")
    tipo_servico = request.form.get("tipo_servico")
    data = request.form.get("data")
    horario = request.form.get("horario")
    descricao = request.form.get("descricao")
    observacoes = request.form.get("observacoes")

    print("\n📅 AGENDAMENTO RECEBIDO:")
    print("Nome:", nome)
    print("Telefone:", telefone)
    print("Email:", email)
    print("Marca:", marca)
    print("Modelo:", modelo)
    print("Ano:", ano)
    print("Placa:", placa)
    print("Tipo de serviço:", tipo_servico)
    print("Data:", data)
    print("Horário:", horario)
    print("Descrição:", descricao)
    print("Observações:", observacoes)

    return "Recebido (Agendamento)"