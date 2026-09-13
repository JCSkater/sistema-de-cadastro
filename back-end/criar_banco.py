import sqlite3

# Conecta ao banco de dados (se o arquivo não existir, ele será criado automaticamente)
conexao = sqlite3.connect('usuarios.db')

# O cursor é o que nos permite executar comandos SQL no banco
cursor = conexao.cursor()

# Cria a tabela de usuários se ela ainda não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
)
''')

# Salva as alterações e fecha a conexão
conexao.commit()
conexao.close()

print("Banco de dados e tabela 'usuarios' criados com sucesso!")
