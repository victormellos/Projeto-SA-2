from flask import render_template, request, redirect, session, flash
from app import app, get_db
import bcrypt
import sqlite3
from datetime import datetime

@app.route('/admin/ordens')
def admin_ordens():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT o.id_ordem, c.nome_cliente, v.modelo, v.placa, 
               o.tipo_ordem, o.status, o.abertura, o.orcamento
        FROM ordem o
        LEFT JOIN clientes c ON o.id_cliente = c.id_cliente
        LEFT JOIN veiculos v ON o.id_veiculo = v.id_veiculo
        ORDER BY o.abertura DESC
    """)
    ordens = cursor.fetchall()
    
    return render_template('admin/admin_ordens.html', 
                         ordens=ordens, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/editar/ordem/<int:id_ordem>', methods=['GET', 'POST'])
def editar_ordem(id_ordem):
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        status = request.form.get('status')
        diagnostico = request.form.get('diagnostico')
        mao_obra = request.form.get('mao_obra')
        orcamento = request.form.get('orcamento')
        
        cursor.execute("""
            UPDATE ordem 
            SET status=?, diagnostico=?, mao_de_obra=?, orcamento=?
            WHERE id_ordem=?
        """, (status, diagnostico, mao_obra, orcamento, id_ordem))
        
        conn.commit()
        
        id_funcionario = session.get("id_funcionario")
        momento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO logs (id_funcionario, detalhe, momento_acao)
            VALUES (?, ?, ?)
        """, (id_funcionario, f'Atualizou ordem #{id_ordem}', momento))
        conn.commit()
        
        flash('Ordem atualizada com sucesso!', 'success')
        return redirect('/admin/ordens')
    
    cursor.execute("""
        SELECT o.*, c.nome_cliente, v.modelo, v.placa
        FROM ordem o
        LEFT JOIN clientes c ON o.id_cliente = c.id_cliente
        LEFT JOIN veiculos v ON o.id_veiculo = v.id_veiculo
        WHERE o.id_ordem=?
    """, (id_ordem,))
    ordem = cursor.fetchone()
    
    return render_template('editar/ordem.html', 
                         ordem=ordem, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/clientes')
def admin_clientes():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    
    if nivel_acesso not in ['2', '3']:
        flash('Acesso negado', 'error')
        return redirect('/dashboard')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id_cliente, c.nome_cliente, c.CPF, c.celular, c.email,
               GROUP_CONCAT(v.placa, ', ') as placas
        FROM clientes c
        LEFT JOIN veiculos v ON c.id_cliente = v.id_cliente
        GROUP BY c.id_cliente
        ORDER BY c.nome_cliente
    """)
    clientes = cursor.fetchall()
    
    return render_template('admin/admin_clientes.html', 
                         clientes=clientes, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/editar/cliente/<int:id_cliente>', methods=['GET', 'POST'])
def editar_cliente(id_cliente):
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    
    if nivel_acesso not in ['2', '3']:
        flash('Acesso negado', 'error')
        return redirect('/dashboard')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        celular = request.form.get('celular')
        
        if nivel_acesso == '3':
            email = request.form.get('email')
            cursor.execute("""
                UPDATE clientes 
                SET nome_cliente=?, CPF=?, celular=?, email=?
                WHERE id_cliente=?
            """, (nome, cpf, celular, email, id_cliente))
        else:
            cursor.execute("""
                UPDATE clientes 
                SET nome_cliente=?, CPF=?, celular=?
                WHERE id_cliente=?
            """, (nome, cpf, celular, id_cliente))
        
        conn.commit()
        
        id_funcionario = session.get("id_funcionario")
        momento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO logs (id_funcionario, detalhe, momento_acao)
            VALUES (?, ?, ?)
        """, (id_funcionario, f'Atualizou cliente {nome}', momento))
        conn.commit()
        
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect('/admin/clientes')
    
    cursor.execute("SELECT * FROM clientes WHERE id_cliente=?", (id_cliente,))
    cliente = cursor.fetchone()
    
    cursor.execute("SELECT * FROM veiculos WHERE id_cliente=?", (id_cliente,))
    veiculos = cursor.fetchall()
    
    return render_template('editar/cliente.html', 
                         cliente=cliente, 
                         veiculos=veiculos,
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/estoque')
def admin_estoque():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id_produto, nome, preco, stock, categoria
        FROM produtos
        ORDER BY nome
    """)
    produtos = cursor.fetchall()
    
    return render_template('admin/admin_estoque.html', 
                         produtos=produtos, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/editar/estoque/<int:id_produto>', methods=['GET', 'POST'])
def editar_estoque(id_produto):
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    
    if nivel_acesso not in ['1', '3']:
        flash('Acesso negado', 'error')
        return redirect('/dashboard')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        preco = request.form.get('preco')
        stock = request.form.get('stock')
        
        if nivel_acesso == '3':
            categoria = request.form.get('categoria')
            cursor.execute("""
                UPDATE produtos 
                SET nome=?, preco=?, stock=?, categoria=?
                WHERE id_produto=?
            """, (nome, preco, stock, categoria, id_produto))
        else:
            cursor.execute("""
                UPDATE produtos 
                SET stock=?
                WHERE id_produto=?
            """, (stock, id_produto))
        
        conn.commit()
        
        id_funcionario = session.get("id_funcionario")
        momento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO logs (id_funcionario, detalhe, momento_acao)
            VALUES (?, ?, ?)
        """, (id_funcionario, f'Atualizou estoque do produto {nome}', momento))
        conn.commit()
        
        flash('Estoque atualizado com sucesso!', 'success')
        return redirect('/admin/estoque')
    
    cursor.execute("SELECT * FROM produtos WHERE id_produto=?", (id_produto,))
    produto = cursor.fetchone()
    
    return render_template('editar/estoque.html', 
                         produto=produto, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/funcionarios')
def admin_funcionarios():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    
    if nivel_acesso != '3':
        flash('Acesso restrito ao gerente', 'error')
        return redirect('/dashboard')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id_funcionario, nome_funcionario, nivel_de_acesso
        FROM funcionarios
        ORDER BY nome_funcionario
    """)
    funcionarios = cursor.fetchall()
    
    return render_template('admin/admin_funcionarios.html', 
                         funcionarios=funcionarios, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/editar/funcionario/<int:id_funcionario>', methods=['GET', 'POST'])
def editar_funcionario(id_funcionario):
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    
    if nivel_acesso != '3':
        flash('Acesso restrito ao gerente', 'error')
        return redirect('/dashboard')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        nivel = request.form.get('nivel')
        nova_senha = request.form.get('senha')
        
        if nova_senha:
            senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                UPDATE funcionarios 
                SET nome_funcionario=?, nivel_de_acesso=?, senha=?
                WHERE id_funcionario=?
            """, (nome, nivel, senha_hash, id_funcionario))
        else:
            cursor.execute("""
                UPDATE funcionarios 
                SET nome_funcionario=?, nivel_de_acesso=?
                WHERE id_funcionario=?
            """, (nome, nivel, id_funcionario))
        
        conn.commit()
        
        id_func_logado = session.get("id_funcionario")
        momento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO logs (id_funcionario, detalhe, momento_acao)
            VALUES (?, ?, ?)
        """, (id_func_logado, f'Atualizou funcionário {nome}', momento))
        conn.commit()
        
        flash('Funcionário atualizado com sucesso!', 'success')
        return redirect('/admin/funcionarios')
    
    cursor.execute("SELECT * FROM funcionarios WHERE id_funcionario=?", (id_funcionario,))
    funcionario = cursor.fetchone()
    
    return render_template('editar/funcionario.html', 
                         funcionario=funcionario, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route("/admin/adicionar/funcionario", methods=["GET", "POST"])
def adicionar_funcionario():
    if session.get("nivel_acesso") != '3':
        return redirect("/dashboard")

    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]
        nivel = request.form["nivel"]

        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO funcionarios (nome_funcionario, senha, nivel_de_acesso) VALUES (?, ?, ?)",
            (nome, senha_hash, nivel)
        )
        conn.commit()

        return redirect("/admin/funcionarios")

    return render_template("admin/adicionar_funcionario.html")

@app.route("/admin/deletar/funcionario/<int:id_funcionario>")
def deletar_funcionario(id_funcionario):
    if session.get("nivel_acesso") != '3':
        return redirect("/dashboard")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM funcionarios WHERE id_funcionario = ?",
        (id_funcionario,)
    )
    conn.commit()

    return redirect("/admin/funcionarios")

@app.route("/admin/adicionar/cliente", methods=["GET", "POST"])
def admin_clientes_adicionar():
    if session.get("tipo") != "funcionario":
        flash("Acesso restrito a funcionários", "error")
        return redirect("/auth/login")

    nivel = session.get("nivel_acesso", "1")
    if nivel not in ["2", "3"]:
        flash("Acesso negado", "error")
        return redirect("/dashboard")

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        celular = request.form.get("celular")
        email = request.form.get("email")

        senha = request.form.get("senha")  

        if not senha:
            flash("A senha é obrigatória!", "error")
            return redirect("/admin/adicionar/cliente")
        

        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

        placa = request.form.get("placa")
        modelo = request.form.get("modelo")
        marca = request.form.get("marca")
        ano = request.form.get("ano")
        cor = request.form.get("cor")

        cursor.execute("""
            INSERT INTO clientes (nome_cliente, CPF, celular, email, senha) 
            VALUES (?, ?, ?, ?, ?)
        """, (nome, cpf, celular, email, senha_hash))
        conn.commit()

        id_cliente = cursor.lastrowid

        if placa or modelo:
            cursor.execute("""
                INSERT INTO veiculos (id_cliente, placa, modelo, marca, ano, cor) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_cliente, placa, modelo, marca, ano, cor))
            conn.commit()

        flash("Cliente cadastrado com sucesso!", "success")
        return redirect("/admin/clientes")

    return render_template(
        "admin/adicionar_cliente.html",
        nivel_acesso=nivel,
        usuario_logado=session.get("usuario")
    )

    print(f"[LOG] Cliente cadastrado: {nome} | CPF: {cpf} | ID: {id_cliente}")


@app.route("/admin/excluir/cliente/<int:id_cliente>")
def excluir_cliente(id_cliente):
    if session.get("tipo") != "funcionario":
        return redirect("/auth/login")

    if session.get("nivel_acesso") not in ["2", "3"]:
        return redirect("/dashboard")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
    conn.commit()

    return redirect("/admin/clientes")


@app.route('/admin/adicionar/estoque', methods=['GET', 'POST'])
def adicionar_produto():
    if session.get("tipo") != "funcionario":
        flash("Acesso restrito", "error")
        return redirect("/auth/login")

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        nome = request.form.get("nome_peca")
        quantidade = request.form.get("quantidade")
        tipo = request.form.get("tipo")
        fornecedor = request.form.get("id_fornecedor")

        cursor.execute("""
            INSERT INTO pecas (nome_peca, quantidade, tipo, id_fornecedor)
            VALUES (?, ?, ?, ?)
        """, (nome, quantidade, tipo, fornecedor))
        conn.commit()

        flash("Peça cadastrada com sucesso!", "success")
        return redirect("/admin/pecas")

    cursor.execute("SELECT * FROM fornecedores")
    fornecedores = cursor.fetchall()

    return render_template(
        "admin/adicionar_produto.html",
        fornecedores=fornecedores,
        usuario_logado=session.get("usuario")
    )

@app.route('/admin/deletar/estoque/<int:id_produto>')
def deletar_produto(id_produto):
    if session.get("tipo") != "funcionario":
        return redirect("/auth/login")

    if session.get("nivel_acesso") not in ["3"]:
        flash("Apenas gerentes podem excluir produtos", "error")
        return redirect("/dashboard")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produtos WHERE id_produto = ?", (id_produto,))
    conn.commit()

    print(f"[LOG] Produto deletado: ID {id_produto}")

    flash("Produto removido com sucesso!", "success")
    return redirect("/admin/estoque")


@app.route('/admin/adicionar/peca', methods=['GET', 'POST'])
def adicionar_peca():
    if session.get("tipo") != "funcionario":
        flash("Acesso restrito a funcionários", "error")
        return redirect("/auth/login")
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == "POST":
        nome_peca = request.form.get("nome_peca")
        quantidade = request.form.get("quantidade")
        tipo = request.form.get("tipo")
        cnpj_fornecedor = request.form.get("cnpj_fornecedor")
        
        cnpj_limpo = cnpj_fornecedor.replace('.', '').replace('/', '').replace('-', '')
        
        cursor.execute("SELECT id_fornecedor FROM fornecedores WHERE cnpj = ?", (cnpj_limpo,))
        fornecedor = cursor.fetchone()
        
        if fornecedor:
            id_fornecedor = fornecedor[0]
        else:
            nome_fornecedor = f"Fornecedor CNPJ: {cnpj_fornecedor}"
            cursor.execute(
                "INSERT INTO fornecedores (nome_fornecedor, cnpj) VALUES (?, ?)",
                (nome_fornecedor, cnpj_limpo)
            )
            conn.commit()
            id_fornecedor = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO pecas (nome_peca, quantidade, tipo, id_fornecedor)
            VALUES (?, ?, ?, ?)
        """, (nome_peca, quantidade, tipo, id_fornecedor))
    
        cursor.execute("""
            INSERT INTO produtos (nome, preco, stock, imagem, categoria, detalhes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nome_peca,
            0.00, 
            quantidade,
            '', 
            'Pecas',
            f'Peça: {tipo if tipo else "Sem tipo especificado"} | Fornecedor: {nome_fornecedor}'
        ))
        
        conn.commit()
        
        id_funcionario = session.get("id_funcionario")
        momento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO logs (id_funcionario, detalhe, momento_acao)
            VALUES (?, ?, ?)
        """, (id_funcionario, f'Adicionou peça: {nome_peca} (estoque: {quantidade})', momento))
        conn.commit()
        
        flash("Peça cadastrada com sucesso no estoque!", "success")
        return redirect("/admin/estoque")
    
    cursor.execute("SELECT * FROM fornecedores")
    fornecedores = cursor.fetchall()
    
    return render_template(
        "admin/adicionar_peca.html",
        fornecedores=fornecedores,
        usuario_logado=session.get("usuario")
    )