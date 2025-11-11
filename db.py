import sqlite3

conn = sqlite3.connect('voto_vivo.db')

cursor = conn.cursor()
print("conectado")

print("DEPUTADOS")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Deputados (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    partido TEXT,
    sigla_uf TEXT,
    url_foto TEXT
);
""")

print("DESPESAS")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Despesas (
    id_deputado INTEGER,
    ano INTEGER,
    mes INTEGER,
    tipo_despesa TEXT,
    valor_liquido REAL,
    FOREIGN KEY (id_deputado) REFERENCES Deputados (id)
);
""")

conn.commit()
conn.close()

print("tabelas criadas")