import sqlite3
'''
AVISO IMPORTANTE
como muitos dados tem UNIQUE, quando você executar o db denovo vai ocorrer um erro de duplicata
então sempre delete o arquivo se for mudar algo
'''
def init_database():
    conn = sqlite3.connect('automax.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;") #Boa prática: usar FOREIGN KEY enforcement Por padrão, o SQLite não ativa chaves estrangeiras.

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
        preco INTEGER NOT NULL,
        stock INTEGER,
        imagem TEXT NOT NULL,
        categoria TEXT NOT NULL

    );
    
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT NOT NULL,
        CPF TEXT UNIQUE NOT NULL,
        celular TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS funcionarios (
        id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_funcionario TEXT NOT NULL,
        nivel_de_acesso INTEGER NOT NULL
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
        conclusao_ordem TEXT,
        mao_de_obra REAL,
        orcamento REAL,
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
    );
    
    CREATE TABLE IF NOT EXISTS funcionario_ordems (
        id_funcionario_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER NOT NULL,
        id_funcionario INTEGER NOT NULL,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem),
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario)
    );
    
    CREATE TABLE IF NOT EXISTS historico_ordems (
        id_historico INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_veiculo INTEGER NOT NULL,
        abertura TEXT,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
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
        FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor)
    );
    
    CREATE TABLE IF NOT EXISTS ordem_pecas (
        id_ordem_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        id_peca INTEGER NOT NULL,
        id_ordem INTEGER NOT NULL,
        quantidade_trocas INTEGER,
        FOREIGN KEY (id_peca) REFERENCES pecas(id_peca),
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem)
    );
    ''')
    
    conn.commit()
    conn.close()

def Inserir_dados():
    conn = sqlite3.connect('automax.db')
    cursor = conn.cursor()

    # Inserindo dados de veiculos
    veiculos = [
        ('Toyota', 'Preto', '2020', 'Corolla', 'ABC-1234'),
        ('Honda', 'Branco', '2021', 'Civic', 'XYZ-5678'),
        ('Ford', 'Azul', '2019', 'Focus', 'DEF-1122'),
        ('Chevrolet', 'Vermelho', '2022', 'Onix', 'JKL-3344'),
        ('Fiat', 'Cinza', '2021', 'Argo', 'MNO-5566'),
        ('Volkswagen', 'Branco', '2018', 'Gol', 'PQR-7788'),
        ('Hyundai', 'Preto', '2022', 'HB20', 'STU-9900'),
        ('Nissan', 'Azul', '2020', 'Versa', 'VWX-1234'),
        ('Renault', 'Amarelo', '2021', 'Sandero', 'YZA-2345'),
        ('Peugeot', 'Verde', '2020', '208', 'BCD-3456'),
        ('Mercedes', 'Cinza', '2022', 'Classe A', 'EFG-4567'),
        ('BMW', 'Preto', '2021', 'X1', 'HIJ-5678'),
        ('Audi', 'Branco', '2019', 'A3', 'KLM-6789'),
        ('Jeep', 'Vermelho', '2022', 'Compass', 'NOP-7890'),
        ('Fiat', 'Laranja', '2019', 'Toro', 'QRS-8901'),
        ('Toyota', 'Azul', '2021', 'Hilux', 'TUV-9012'),
        ('Honda', 'Prata', '2020', 'HR-V', 'WXY-0123'),
        ('Chevrolet', 'Preto', '2021', 'Tracker', 'ZAB-1234'),
        ('Ford', 'Branco', '2020', 'Ecosport', 'CDE-2345')
    ]
    cursor.executemany(''' 
        INSERT INTO veiculos (marca, cor, ano, modelo, placa)
        VALUES (?, ?, ?, ?, ?)
    ''', veiculos)

    # Inserindo dados de produtos
    produtos = [
        ('Óleo de motor', 50, 100, 'óleo_motor.jpg', 'Pecas'),
        ('Filtro de ar', 30, 200, 'filtro_ar.jpg', 'Pecas'),
        ('Pastilha de freio', 70, 150, 'pastilha_freio.jpg', 'Pecas'),
        ('Pneu 205/55', 350, 120, 'pneu_205.jpg', 'Pecas'),
        ('Bateria 60Ah', 200, 80, 'bateria_60Ah.jpg', 'Pecas'),
        ('Amortecedor', 150, 60, 'amortecedor.jpg', 'Pecas'),
        ('Farol de milha', 120, 90, 'farol_milha.jpg', 'Acessorios'),
        ('Lâmpada halógena', 20, 250, 'lampada_halogenas.jpg', 'Acessorios'),
        ('Capa de banco', 50, 300, 'capa_banco.jpg', 'Acessorios'),
        ('Alarme', 100, 80, 'alarme.jpg', 'Acessorios'),
        ('Cinto de segurança', 40, 120, 'cinto_segurança.jpg', 'Acessorios'),
        ('Mola de suspensão', 100, 75, 'mola_suspensao.jpg', 'Pecas'),
        ('Catalisador', 300, 50, 'catalisador.jpg', 'Pecas'),
        ('Sensor de estacionamento', 150, 100, 'sensor_estacionamento.jpg', 'Acessorios'),
        ('Radiador', 250, 60, 'radiador.jpg', 'Pecas'),
        ('Ventoinha', 90, 200, 'ventoinha.jpg', 'Pecas'),
        ('Cárter', 180, 70, 'carter.jpg', 'Pecas'),
        ('Difusor', 60, 110, 'difusor.jpg', 'Acessorios'),
        ('Tampa de válvula', 50, 150, 'tampa_valvula.jpg', 'Pecas'),
        ('Coxim de motor', 120, 80, 'coxim_motor.jpg', 'Pecas')
    ]
    cursor.executemany('''
        INSERT INTO produtos (nome, preco, stock, imagem, categoria)
        VALUES (?, ?, ?, ?, ?)
    ''', produtos)

    # Inserindo dados de clientes (sem duplicatas de CPF)
    clientes = [
        ('João Silva', '123.456.789-00', '123456789', 'joao@email.com', 'senha123'),
        ('Maria Oliveira', '987.654.321-00', '987654321', 'maria@email.com', 'senha456'),
        ('Carlos Souza', '111.222.333-44', '112233445', 'carlos@email.com', 'senha789'),
        ('Ana Costa', '555.444.333-22', '554433221', 'ana@email.com', 'senha101'),
        ('Lucas Pereira', '444.555.666-77', '445566778', 'lucas@email.com', 'senha102'),
        ('Fernanda Lima', '777.888.999-00', '778899001', 'fernanda@email.com', 'senha103'),
        ('Gustavo Mendes', '333.444.555-66', '334455667', 'gustavo@email.com', 'senha104'),
        ('Roberta Martins', '222.333.444-11', '223344556', 'roberta@email.com', 'senha105'),
        ('Ricardo Almeida', '111.000.999-88', '110099880', 'ricardo@email.com', 'senha106'),
        ('Patrícia Santos', '555.666.777-99', '556677889', 'patricia@email.com', 'senha107'),
        ('Márcio Silva', '444.555.666-00', '445566778', 'marcio@email.com', 'senha108'),
        ('Gabriela Costa', '333.444.555-11', '334455667', 'gabriela@email.com', 'senha109'),
        ('Felipe Oliveira', '111.222.333-77', '112233445', 'felipe@email.com', 'senha110'),
        ('Tatiane Rocha', '777.888.999-00', '778899001', 'tatiane@email.com', 'senha111'),
        ('Juliana Santos', '555.444.333-88', '554433221', 'juliana@email.com', 'senha112'),
        ('Marcos Dias', '444.333.222-11', '445566778', 'marcos@email.com', 'senha113'),
        ('Camila Almeida', '333.222.111-44', '334455667', 'camila@email.com', 'senha114'),
        ('Eduardo Silva', '111.000.999-77', '110099880', 'eduardo@email.com', 'senha115'),
        ('Juliano Costa', '777.666.555-66', '778899001', 'juliano@email.com', 'senha116'),
        ('Rafaela Lima', '555.444.333-99', '554433221', 'rafaela@email.com', 'senha117')
    ]

    # Removendo duplicatas de CPF
    seen_cpfs = set()
    clientes_unicos = []
    for cliente in clientes:
        cpf = cliente[1]  # O CPF é o segundo elemento da tupla
        if cpf not in seen_cpfs:
            seen_cpfs.add(cpf)
            clientes_unicos.append(cliente)

    # Inserindo clientes sem duplicatas
    cursor.executemany('''
        INSERT INTO clientes (nome_cliente, CPF, celular, email, senha)
        VALUES (?, ?, ?, ?, ?)
    ''', clientes_unicos)

    # Inserindo dados de funcionarios
    funcionarios = [
        ('José Pereira', 1),
        ('Mariana Souza', 2),
        ('Roberto Lima', 3),
        ('Carla Oliveira', 1),
        ('Carlos Costa', 2),
        ('Luana Martins', 3),
        ('Felipe Almeida', 1),
        ('Sérgio Silva', 2),
        ('Fernanda Dias', 3),
        ('Ricardo Pereira', 1),
        ('Ana Costa', 2),
        ('Patrícia Silva', 3),
        ('Marcos Almeida', 1),
        ('Tatiane Costa', 2),
        ('Gustavo Lima', 3),
        ('Lucas Almeida', 1),
        ('Juliana Silva', 2),
        ('Rafaela Costa', 3),
        ('Márcio Silva', 1),
        ('Camila Costa', 2)
    ]
    cursor.executemany('''
        INSERT INTO funcionarios (nome_funcionario, nivel_de_acesso)
        VALUES (?, ?)
    ''', funcionarios)

    # Commit e fechamento da conexão
    conn.commit()
    conn.close()





if __name__ == '__main__':
    init_database()
    Inserir_dados()
    



