import sqlite3
from datetime import datetime

# Conecta ao banco de dados (se não existir, o SQLite cria o arquivo na hora)
conn = sqlite3.connect('estoque_pro.db', check_same_thread=False)
cursor = conn.cursor()

def inicializar_banco():
    """Cria as tabelas do sistema caso elas ainda não existam."""
    
    # Tabela 1: Catálogo de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            sku TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT,
            estoque_minimo INTEGER DEFAULT 0,
            estoque_atual INTEGER DEFAULT 0
        )
    ''')

    # Tabela 2: Histórico de Movimentações (Entradas, Saídas e Balanços)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT,
            tipo TEXT NOT NULL, -- 'ENTRADA', 'SAIDA', 'CONTAGEM_INICIAL'
            quantidade INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            usuario TEXT DEFAULT 'Sistema',
            FOREIGN KEY (sku) REFERENCES produtos(sku)
        )
    ''')
    
    conn.commit()
    print("Banco de dados inicializado com sucesso!")

def adicionar_produto_teste():
    """Função temporária para colocar alguns dados no banco e podermos testar a interface depois."""
    produtos_iniciais = [
        ('ARD-001', 'Arduino Uno R3', 'Placas', 10, 45),
        ('RASP-04', 'Raspberry Pi 4', 'Placas', 5, 3), # Estoque crítico!
        ('CAB-HDMI', 'Cabo HDMI 2m', 'Cabos', 20, 25),
        ('MULT-DIG', 'Multímetro Digital', 'Ferramentas', 2, 5)
    ]
    
    # O comando 'INSERT OR IGNORE' evita erro se você rodar o script duas vezes
    cursor.executemany('''
        INSERT OR IGNORE INTO produtos (sku, nome, categoria, estoque_minimo, estoque_atual)
        VALUES (?, ?, ?, ?, ?)
    ''', produtos_iniciais)
    
    conn.commit()
    print(" Produtos de teste inseridos!")

# Executa as funções se você rodar este arquivo diretamente
if __name__ == "__main__":
    inicializar_banco()
    adicionar_produto_teste()