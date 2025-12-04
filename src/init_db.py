import sqlite3

conn = sqlite3.connect('automax.db')
cursor = conn.cursor() 

def init_database():
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript(''' 
    CREATE TABLE IF NOT EXISTS veiculos (
        id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        cor TEXT NOT NULL,
        ano TEXT NOT NULL,
        modelo TEXT NOT NULL,
        placa TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS produtos (
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,  
        preco REAL NOT NULL,
        stock INTEGER,
        imagem TEXT NOT NULL,
        categoria TEXT NOT NULL,
        detalhes TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT NOT NULL,
        CPF TEXT UNIQUE NOT NULL,
        celular TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha BLOB NOT NULL
    );

    CREATE TABLE IF NOT EXISTS funcionarios (
        id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
        senha BLOB NOT NULL,
        nome_funcionario TEXT NOT NULL,
        nivel_de_acesso TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ordem (
        id_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_funcionario INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_veiculo INTEGER NOT NULL,
        tipo_ordem TEXT NOT NULL,
        diagnostico TEXT,
        abertura TEXT,
        prazo TEXT,
        fechamento TEXT,
        mao_de_obra REAL,
        orcamento REAL,
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario) ON DELETE CASCADE,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS logs_fun(
        id_logs_fun INTEGER PRIMARY KEY AUTOINCREMENT,
        id_func INTEGER,
        id_log INTEGER,
        FOREIGN KEY (id_func) REFERENCES funcionarios(id_funcionario) ON DELETE SET NULL
        FOREIGN KEY (id_log) REFERENCES logs(id_log) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS logs (
        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
        id_funcionario INTEGER,
        detalhe TEXT,
        momento_acao TEXT,
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS funcionario_ordems (
        id_funcionario_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER NOT NULL,
        id_funcionario INTEGER NOT NULL,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem) ON DELETE CASCADE,
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS historico_ordems (
        id_historico INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_veiculo INTEGER NOT NULL,
        abertura TEXT,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem) ON DELETE CASCADE,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS fornecedores (
        id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_fornecedor TEXT NOT NULL,
        cnpj TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pecas (
        id_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_peca TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        tipo TEXT,
        id_fornecedor INTEGER NOT NULL,
        FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ordem_pecas (
        id_ordem_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        id_peca INTEGER NOT NULL,
        id_ordem INTEGER NOT NULL,
        quantidade_trocas INTEGER,
        FOREIGN KEY (id_peca) REFERENCES pecas(id_peca) ON DELETE CASCADE,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem) ON DELETE CASCADE
    );
    ''')

    conn.commit()

def Inserir_dados():
    veiculos = [
        ('Toyota', 'Preto', '2020', 'Corolla', 'ABC-1234'),
        ('Honda', 'Branco', '2021', 'Civic', 'XYZ-5678'),
    ]
    cursor.executemany(''' 
        INSERT INTO veiculos (marca, cor, ano, modelo, placa)
        VALUES (?, ?, ?, ?, ?)
    ''', veiculos)

    produtos = [
        ('Óleo de motor', 50, 100, 'óleo_motor.jpg', 'Pecas', 'Óleo para motores de carros, ideal para troca de óleo.'),
        ('Filtro de ar', 30, 200, 'filtro_ar.jpg', 'Pecas', 'Filtro de ar para manter o motor livre de impurezas.'),
        ('Pastilha de freio', 70, 150, 'pastilha_freio.jpg', 'Pecas', 'Pastilhas de freio de alta performance, seguras e duráveis.'),
        ('Pneu 205/55', 350, 120, 'pneu_205.jpg', 'Pecas', 'Pneu de alta resistência para carros de passeio.'),
        ('Bateria 60Ah', 200, 80, 'bateria_60Ah.jpg', 'Pecas', 'Bateria automotiva de 60Ah, ideal para carros populares.'),
        ('Amortecedor', 150, 60, 'amortecedor.jpg', 'Pecas', 'Amortecedor para melhorar a suspensão do veículo.'),
        ('Farol de milha', 120, 90, 'farol_milha.jpg', 'Acessorios', 'Farol de milha para visibilidade em condições adversas.'),
        ('Lâmpada halógena', 20, 250, 'lampada_halogenas.jpg', 'Acessorios', 'Lâmpada halógena com alta durabilidade e luminosidade.'),
        ('Capa de banco', 50, 300, 'capa_banco.jpg', 'Acessorios', 'Capa protetora para bancos de carro, disponível em várias cores.'),
        ('Alarme', 100, 80, 'alarme.jpg', 'Acessorios', 'Sistema de alarme automotivo com sensores de movimento e distância.'),
        ('Cinto de segurança', 40, 120, 'cinto_segurança.jpg', 'Acessorios', 'Cinto de segurança confortável e com ajuste de tamanho.'),
        ('Mola de suspensão', 100, 75, 'mola_suspensao.jpg', 'Pecas', 'Mola de suspensão de alta resistência para estabilidade do veículo.'),
        ('Catalisador', 300, 50, 'catalisador.jpg', 'Pecas', 'Catalisador para reduzir as emissões de poluentes do veículo.'),
        ('Sensor de estacionamento', 150, 100, 'sensor_estacionamento.jpg', 'Acessorios', 'Sensor de estacionamento com alerta sonoro para facilitar manobras.'),
        ('Radiador', 250, 60, 'radiador.jpg', 'Pecas', 'Radiador de alta performance para controle da temperatura do motor.'),
        ('Ventoinha', 90, 200, 'ventoinha.jpg', 'Pecas', 'Ventoinha para resfriamento eficiente do sistema de arrefecimento do motor.'),
        ('Cárter', 180, 70, 'carter.jpg', 'Pecas', 'Cárter para proteção do motor e armazenamento de óleo lubrificante.'),
        ('Difusor', 60, 110, 'difusor.jpg', 'Acessorios', 'Difusor de ar para melhorar a circulação do ar no interior do veículo.'),
        ('Tampa de válvula', 50, 150, 'tampa_valvula.jpg', 'Pecas', 'Tampa de válvula para vedação do motor e prevenção de vazamentos.'),
        ('Coxim de motor', 120, 80, 'coxim_motor.jpg', 'Pecas', 'Coxim de motor para redução de vibrações e ruídos no veículo.')
    ]
    
    cursor.executemany(''' 
        INSERT INTO produtos (nome, preco, stock, imagem, categoria, detalhes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', produtos)

    clientes = [
        ('João Silva', '123.456.789-00', '123456789', 'joao@email.com', '$2a$12$pYP4kAD2vLNv4zjeksgvae0KdACRpI7CN08/fq.wB6DtoMCEKwbf6'.encode("utf-8")),
        ('Maria Oliveira', '987.654.321-00', '987654321', 'maria@email.com', '$2a$12$pYP4kAD2vLNv4zjeksgvae0KdACRpI7CN08/fq.wB6DtoMCEKwbf6'.encode("utf-8")),
    ]
    
    cursor.executemany(''' 
        INSERT INTO clientes (nome_cliente, CPF, celular, email, senha)
        VALUES (?, ?, ?, ?, ?)
    ''', clientes)

    funcionarios = [
        ('$2a$12$GDvXuhxPgDCeVHxNSDuEiOLB/sS4DLhnN7b80PlUSCeJtGNz/NXb6'.encode("UTF-8"), 'Carlos Mendes', '3'),
        ('$2a$12$BeKxQu2T1M7SdWDNCtvdN.7ButNJTX1gUsGhRBz7fiJl1lqfHcClS'.encode("UTF-8"), 'Roberto Santos', '2'),
        ('$2a$12$CpGfc6d35zl.f/VcykquV.eKQKS5wrqSUuXbGWYarVjzQ1YcIkVMe'.encode("UTF-8"), 'Ana Costa', '1')
    ]
    
    cursor.executemany(''' 
        INSERT INTO funcionarios (senha, nome_funcionario, nivel_de_acesso)
        VALUES (?, ?, ?)
    ''', funcionarios)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
    Inserir_dados()
