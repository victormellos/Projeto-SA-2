from flask import render_template, request, redirect, session, flash
from app import app, get_db
import bcrypt
import sqlite3
from datetime import datetime

@app.route('/admin')
@app.route('/dashboard')
def dashboard():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
    usuario = session.get("usuario")
    nivel_acesso = session.get("nivel_acesso", "1")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM ordem WHERE status IN ('EM ANDAMENTO', 'AGUARDANDO PEÇA', 'EM ABERTO')")
        ordens_abertas = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM produtos WHERE stock < 10")
        produtos_baixo_estoque = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM clientes")
        clientes_ativos = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT 
                strftime('%Y-%m', o.abertura) as mes,
                SUM(o.orcamento) as receita
            FROM ordem o
            WHERE o.abertura IS NOT NULL 
            AND o.abertura >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', o.abertura)
            ORDER BY mes
        """)
        receita_mensal = cursor.fetchall()

        meses = []
        receitas = []
        for row in receita_mensal:
            if row[0]:
                mes_formatado = datetime.strptime(row[0], '%Y-%m').strftime('%b')
                meses.append(mes_formatado)
                receitas.append(float(row[1]) if row[1] else 0)

        while len(meses) < 6:
            meses.insert(0, '')
            receitas.insert(0, 0)

        receita_mes_atual = receitas[-1] if receitas else 0

        cursor.execute("""
            SELECT o.id_ordem, c.nome_cliente, v.modelo, v.placa, o.status 
            FROM ordem o
            LEFT JOIN clientes c ON o.id_cliente = c.id_cliente
            LEFT JOIN veiculos v ON o.id_veiculo = v.id_veiculo
            WHERE o.status != 'CONCLUIDO'
            ORDER BY o.abertura DESC
            LIMIT 4
        """)
        ordens_pendentes = cursor.fetchall()
        
        cursor.execute("""
            SELECT nome, stock, 
                CASE 
                    WHEN stock < 5 THEN 'Crítico'
                    WHEN stock < 10 THEN 'Baixo'
                    ELSE 'Normal'
                END as status_estoque
            FROM produtos 
            WHERE stock < 15
            ORDER BY stock ASC
            LIMIT 4
        """)
        produtos_estoque = cursor.fetchall()

        cursor.execute("""
            SELECT o.id_ordem, c.nome_cliente, o.tipo_ordem, o.abertura
            FROM ordem o
            LEFT JOIN clientes c ON o.id_cliente = c.id_cliente
            ORDER BY o.abertura DESC
            LIMIT 5
        """)
        atividades_recentes = cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Erro no banco: {e}")
        ordens_abertas = 0
        produtos_baixo_estoque = 0
        clientes_ativos = 0
        meses = ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        receitas = [32000, 28500, 35000, 41000, 37200, 45800]
        receita_mes_atual = 45800
        ordens_pendentes = []
        produtos_estoque = []
        atividades_recentes = []
    
    return render_template(
        'dashboard.html',
        usuario_logado=usuario,
        nivel_acesso=nivel_acesso,
        ordens_abertas=ordens_abertas,
        produtos_baixo_estoque=produtos_baixo_estoque,
        clientes_ativos=clientes_ativos,
        receita_mes_atual=receita_mes_atual,
        meses=meses,
        receitas=receitas,
        ordens_pendentes=ordens_pendentes,
        produtos_estoque=produtos_estoque,
        atividades_recentes=atividades_recentes
    )

@app.route('/admin/ordens')
def admin_ordens():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
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
    
    return render_template('admin_ordens.html', 
                         ordens=ordens, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/ordens/editar/<int:id_ordem>', methods=['GET', 'POST'])
def editar_ordem(id_ordem):
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
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
    
    return render_template('editar_ordem.html', 
                         ordem=ordem, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/clientes')
def admin_clientes():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
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
    
    return render_template('admin_clientes.html', 
                         clientes=clientes, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/clientes/editar/<int:id_cliente>', methods=['GET', 'POST'])
def editar_cliente(id_cliente):
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
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
    
    return render_template('editar_cliente.html', 
                         cliente=cliente, 
                         veiculos=veiculos,
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/estoque')
def admin_estoque():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
    nivel_acesso = session.get("nivel_acesso", "1")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id_produto, nome, preco, stock, categoria
        FROM produtos
        ORDER BY nome
    """)
    produtos = cursor.fetchall()
    
    return render_template('admin_estoque.html', 
                         produtos=produtos, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/estoque/editar/<int:id_produto>', methods=['GET', 'POST'])
def editar_estoque(id_produto):
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
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
    
    return render_template('editar_estoque.html', 
                         produto=produto, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/funcionarios')
def admin_funcionarios():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
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
    
    return render_template('admin_funcionarios.html', 
                         funcionarios=funcionarios, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))

@app.route('/admin/funcionarios/editar/<int:id_funcionario>', methods=['GET', 'POST'])
def editar_funcionario(id_funcionario):
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
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
        """, (id_func_logado, f'Atualizo    u funcionário {nome}', momento))
        conn.commit()
        
        flash('Funcionário atualizado com sucesso!', 'success')
        return redirect('/admin/funcionarios')
    
    cursor.execute("SELECT * FROM funcionarios WHERE id_funcionario=?", (id_funcionario,))
    funcionario = cursor.fetchone()
    
    return render_template('editar_funcionario.html', 
                         funcionario=funcionario, 
                         nivel_acesso=nivel_acesso,
                         usuario_logado=session.get("usuario"))