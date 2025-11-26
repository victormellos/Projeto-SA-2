import sqlite3

def init_database():
    conn = sqlite3.connect('automax.db')
    cursor = conn.cursor()
    
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS veiculos (
        id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT,
        cor TEXT,
        ano TEXT,
        modelo TEXT,
        placa TEXT UNIQUE
    );
    
    CREATE TABLE IF NOT EXISTS produtos (
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco INTEGER,
        stock INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT,
        CPF TEXT UNIQUE,
        celular TEXT,
        email TEXT UNIQUE,
        senha TEXT
    );
    
    CREATE TABLE IF NOT EXISTS funcionarios (
        id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_funcionario TEXT,
        nivel_de_acesso INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS ordem (
        id_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_funcionario INTEGER,
        id_cliente INTEGER,
        id_veiculo INTEGER,
        tipo_ordem TEXT,
        diagnostico TEXT,
        abertura TEXT,
        prazo TEXT,
        fechamento TEXT,
        conclusao_ordem TEXT,
        mao_de_obra REAL,
        orcamento REAL,
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
    );
    
    CREATE TABLE IF NOT EXISTS funcionario_ordems (
        id_funcionario_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER,
        id_funcionario INTEGER,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem),
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario)
    );
    
    CREATE TABLE IF NOT EXISTS historico_ordems (
        id_historico INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER,
        id_cliente INTEGER,
        id_veiculo INTEGER,
        abertura TEXT,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
    );
    
    CREATE TABLE IF NOT EXISTS fornecedores (
        id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_fornecedor TEXT,
        cnpj TEXT UNIQUE
    );
    
    CREATE TABLE IF NOT EXISTS pecas (
        id_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_peca TEXT,
        quantidade INTEGER,
        tipo TEXT,
        id_fornecedor INTEGER,
        FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor)
    );
    
    CREATE TABLE IF NOT EXISTS ordem_pecas (
        id_ordem_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        id_peca INTEGER,
        id_ordem INTEGER,
        quantidade_trocas INTEGER,
        FOREIGN KEY (id_peca) REFERENCES pecas(id_peca),
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem)
    );
    
   INSERT INTO veiculos (marca, cor, ano, modelo, placa) VALUES
('Toyota', 'Prata', '2018', 'Corolla', 'ABC1D23'),
('Honda', 'Preto', '2020', 'Civic', 'EFG4H56'),
('Ford', 'Branco', '2015', 'Focus', 'IJK7L89'),
('Chevrolet', 'Vermelho', '2019', 'Onix', 'MNO3P45');

INSERT INTO produtos (nome, preco, stock) VALUES
('Óleo 5W30', 45, 30),
('Filtro de Ar', 25, 50),
('Bateria 60Ah', 350, 12),
('Limpador de Para-brisa', 18, 40);

INSERT INTO clientes (nome_cliente, CPF, celular, email, senha) VALUES
('Carlos Alberto', '12345678901', '11987654321', 'carlos@email.com', 'senha123'),
('Mariana Souza', '98765432100', '11911112222', 'mariana@email.com', 'senha123'),
('Ricardo Lima', '45678912366', '11933334444', 'ricardo@email.com', 'senha123');

INSERT INTO funcionarios (nome_funcionario, nivel_de_acesso) VALUES
('João Mecânico', 1),
('Fernanda Gerente', 3),
('Paulo Eletricista', 1);

INSERT INTO ordem (
    id_funcionario, id_cliente, id_veiculo,
    tipo_ordem, diagnostico, abertura, prazo, fechamento,
    conclusao_ordem, mao_de_obra, orcamento
)
VALUES
(1, 1, 1, 'Revisão', 'Troca de óleo e filtros', '2025-01-05', '2025-01-06', '2025-01-06', 'Serviço finalizado', 150.00, 250.00),
(2, 2, 2, 'Elétrica', 'Falha na ignição', '2025-01-10', '2025-01-12', NULL, NULL, 200.00, 480.00),
(3, 3, 3, 'Mecânica', 'Barulho na suspensão', '2025-01-02', '2025-01-05', '2025-01-05', 'Trocado amortecedor', 300.00, 750.00);

INSERT INTO funcionario_ordems (id_ordem, id_funcionario) VALUES
(1, 1),
(2, 2),
(3, 3),
(3, 1);

INSERT INTO historico_ordems (id_ordem, id_cliente, id_veiculo, abertura) VALUES
(1, 1, 1, '2025-01-05'),
(3, 3, 3, '2025-01-02');

INSERT INTO fornecedores (nome_fornecedor, cnpj) VALUES
('AutoParts Brasil', '11222333000144'),
('Fornec Peças Ltda', '99888777000122');

INSERT INTO pecas (nome_peca, quantidade, tipo, id_fornecedor) VALUES
('Filtro de Óleo', 20, 'Motor', 1),
('Pastilha de Freio', 15, 'Freios', 1),
('Amortecedor Dianteiro', 8, 'Suspensão', 2),
('Velas de Ignição', 25, 'Elétrica', 2);

INSERT INTO ordem_pecas (id_peca, id_ordem, quantidade_trocas) VALUES
(1, 1, 1),
(4, 2, 4),
(3, 3, 2);

    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
    



