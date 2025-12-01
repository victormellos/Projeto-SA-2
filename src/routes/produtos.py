import sqlite3
from flask import render_template, jsonify
from app import app
from app import get_db

DATABASE = 'automax.db'

@app.route('/produtos/<int:id>')
def get_product(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT id_produto, nome, preco, stock
        FROM produtos
        WHERE id_produto = ?
    ''', (id,))  

    produto = cursor.fetchone()

    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto_dict = {
        "id": produto[0],
        "nome": produto[1],
        "preco": produto[2],
        "stock": produto[3]
    }

    return jsonify(produto_dict)