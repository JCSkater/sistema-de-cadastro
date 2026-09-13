from flask import Flask, request, jsonify
from flask_cors import CORS
from criar_banco import criar_banco  # Importa a função para criar o banco de dados
import html  # Biblioteca nativa para sanitizar HTML/XSS
import re    # Biblioteca nativa para expressões regulares (Regex)
import sqlite3 # Biblioteca nativa para o banco de dados
import bcrypt # Biblioteca para criptografia de senhas (Hashing)
import os

app = Flask(__name__)
CORS(app)

# Expressão regular para validar o formato do e-mail no servidor
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
# Expressão regular para validar o nome (apenas letras e espaços, de 3 a 50 caracteres)
NOME_REGEX = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]{3,50}$"

# Cria o banco de dados e a tabela se não existirem
criar_banco()

# Nome do arquivo do banco de dados
DB_NAME = 'usuarios.db'

@app.route("/")
def home():
    return "Olá! O seu servidor Back-End em Python está funcionando localmente, com senhas protegidas por BCrypt!"

# --- ENDPOINT DE LOGIN ---
@app.route("/login", methods=["POST"])
def login_endpoint():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"status": "erro", "mensagem": "Requisição inválida."}), 400
            
        email_bruto = dados.get("email", "").strip()
        senha_digitada = dados.get("senha")
        
        # 1. VALIDAÇÃO NO SERVIDOR
        if not email_bruto or not senha_digitada:
            return jsonify({"status": "erro", "mensagem": "E-mail e senha são obrigatórios!"}), 400
            
        # 2. SANITIZAÇÃO NO SERVIDOR
        email_sanitizado = html.escape(email_bruto)
        
        # 3. VALIDAÇÃO DE FORMATO
        if not re.match(EMAIL_REGEX, email_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Formato de e-mail inválido!"}), 400

        # --- CONEXÃO COM O BANCO ---
        conexao = sqlite3.connect(DB_NAME)
        cursor = conexao.cursor()
        
        # Busca o hash da senha guardado no banco para este e-mail
        cursor.execute("SELECT senha FROM usuarios WHERE email = ?", (email_sanitizado,))
        resultado = cursor.fetchone()
        conexao.close()

        if resultado:
            senha_criptografada_banco = resultado[0]
            
            # Como o SQLite salva como texto, precisamos converter a senha do banco de volta para bytes
            senha_banco_bytes = senha_criptografada_banco.encode('utf-8')
            senha_digitada_bytes = senha_digitada.encode('utf-8')

            # O Bcrypt compara se a senha digitada corresponde ao hash gerado anteriormente
            if bcrypt.checkpw(senha_digitada_bytes, senha_banco_bytes):
                return jsonify({"status": "sucesso", "mensagem": "Login autorizado!"}), 200

        # Retorna o mesmo erro genérico se o e-mail não existir ou a senha estiver errada (Boa prática de segurança)
        return jsonify({"status": "erro", "mensagem": "E-mail ou senha incorretos."}), 401

    except Exception as e:
        print(f"[ERRO CRÍTICO NO LOGIN]: {str(e)}")
        return jsonify({"status": "erro", "mensagem": "Ocorreu um erro interno ao processar o seu login."}), 500


# --- ENDPOINT DE CADASTRO ---
@app.route("/cadastro", methods=["POST"])
def cadastro_endpoint():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"status": "erro", "mensagem": "Requisição inválida."}), 400
            
        nome_bruto = dados.get("nome", "").strip()
        email_bruto = dados.get("email", "").strip()
        senha_bruta = dados.get("senha")
        
        # 1. VALIDAÇÃO: Verifica preenchimento
        if not nome_bruto or not email_bruto or not senha_bruta:
            return jsonify({"status": "erro", "mensagem": "Todos os campos são obrigatórios!"}), 400
            
        # Limitação de tamanho para evitar ataques de DoS
        if len(nome_bruto) > 50 or len(email_bruto) > 60 or len(senha_bruta) > 32:
            return jsonify({"status": "erro", "mensagem": "Tamanho de dados excedido!"}), 400

        # 2. SANITIZAÇÃO: Limpa contra injeções XSS
        nome_sanitizado = html.escape(nome_bruto)
        email_sanitizado = html.escape(email_bruto)

        # 3. VALIDAÇÃO DE REGEX
        if not re.match(NOME_REGEX, nome_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Nome inválido! Use apenas letras e espaços."}), 400
            
        if not re.match(EMAIL_REGEX, email_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Formato de e-mail inválido!"}), 400

        # --- CRIPTOGRAFIA DA SENHA (NOVO) ---
        # Converte a senha recebida em texto para bytes
        senha_bytes = senha_bruta.encode('utf-8')
        # Gera o salt aleatório e aplica a criptografia hash
        salt = bcrypt.gensalt()
        senha_hash_bytes = bcrypt.hashpw(senha_bytes, salt)
        # Transforma o hash resultante de bytes para texto comum (string) para salvar no SQLite
        senha_criptografada_texto = senha_hash_bytes.decode('utf-8')

        # --- INTEGRAÇÃO COM BANCO DE DADOS ---
        try:
            conexao = sqlite3.connect(DB_NAME)
            cursor = conexao.cursor()
            
            # Insere o novo registro salvando a senha criptografada
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha) 
                VALUES (?, ?, ?)
            ''', (nome_sanitizado, email_sanitizado, senha_criptografada_texto))
            
            conexao.commit()
            conexao.close()
            
            print(f"[SERVER LOG] Novo usuário cadastrado com senha protegida!")
            return jsonify({"status": "sucesso", "mensagem": f"Cadastro de {nome_sanitizado} realizado com sucesso!"}), 201

        except sqlite3.IntegrityError:
            return jsonify({"status": "erro", "mensagem": "Este e-mail já está cadastrado!"}), 400

    except Exception as e:
        print(f"[ERRO CRÍTICO NO CADASTRO]: {str(e)}")
        return jsonify({"status": "erro", "mensagem": "Ocorreu um erro interno ao processar o seu cadastro."}), 500

if __name__ == "__main__":
     # O Render injeta a porta correta na variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
