from flask import Flask, request, jsonify
from flask_cors import CORS
import html  # Biblioteca nativa para sanitizar HTML/XSS
import re    # Biblioteca nativa para expressões regulares (Regex)
import sqlite3 # Biblioteca nativa para o banco de dados

app = Flask(__name__)
CORS(app)

# Expressão regular para validar o formato do e-mail no servidor
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
# Expressão regular para validar o nome (apenas letras e espaços, de 3 a 50 caracteres)
NOME_REGEX = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]{3,50}$"

# Nome do arquivo do banco de dados para facilitar a manutenção
DB_NAME = 'usuarios.db'

@app.route("/")
def home():
    return "Olá! O seu servidor Back-End em Python está funcionando localmente e integrado ao banco de dados!"

# --- ENDPOINT DE LOGIN ---
@app.route("/login", methods=["POST"])
def login_endpoint():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"status": "erro", "mensagem": "Requisição inválida."}), 400
            
        email_bruto = dados.get("email", "").strip()
        senha = dados.get("senha")
        
        # 1. VALIDAÇÃO NO SERVIDOR
        if not email_bruto or not senha:
            return jsonify({"status": "erro", "mensagem": "E-mail e senha são obrigatórios!"}), 400
            
        # 2. SANITIZAÇÃO NO SERVIDOR
        email_sanitizado = html.escape(email_bruto)
        
        # 3. VALIDAÇÃO DE FORMATO
        if not re.match(EMAIL_REGEX, email_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Formato de e-mail inválido!"}), 400

        # --- INTEGRAÇÃO COM BANCO DE DADOS (LOGIN) ---
        conexao = sqlite3.connect(DB_NAME)
        cursor = conexao.cursor()
        
        # Busca o usuário pelo e-mail e verifica a senha (usando placeholders '?' por segurança contra SQL Injection)
        cursor.execute("SELECT senha FROM usuarios WHERE email = ?", (email_sanitizado,))
        resultado = cursor.fetchone()
        conexao.close()

        # Se encontrou o e-mail e a senha digitada confere com a salva no banco
        if resultado and resultado[0] == senha:
            return jsonify({"status": "sucesso", "mensagem": "Login autorizado!"}), 200
        else:
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
        senha = dados.get("senha")
        
        # 1. VALIDAÇÃO: Verifica preenchimento
        if not nome_bruto or not email_bruto or not senha:
            return jsonify({"status": "erro", "mensagem": "Todos os campos são obrigatórios!"}), 400
            
        # Limitação de tamanho para evitar ataques de estouro de dados (DoS)
        if len(nome_bruto) > 50 or len(email_bruto) > 60 or len(senha) > 32:
            return jsonify({"status": "erro", "mensagem": "Tamanho de dados excedido!"}), 400

        # 2. SANITIZAÇÃO: Limpa contra injeções XSS
        nome_sanitizado = html.escape(nome_bruto)
        email_sanitizado = html.escape(email_bruto)

        # 3. VALIDAÇÃO DE REGEX
        if not re.match(NOME_REGEX, nome_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Nome inválido! Use apenas letras e espaços."}), 400
            
        if not re.match(EMAIL_REGEX, email_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Formato de e-mail inválido!"}), 400

        # --- INTEGRAÇÃO COM BANCO DE DADOS (CADASTRO) ---
        try:
            conexao = sqlite3.connect(DB_NAME)
            cursor = conexao.cursor()
            
            # Insere o novo registro
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha) 
                VALUES (?, ?, ?)
            ''', (nome_sanitizado, email_sanitizado, senha))
            
            conexao.commit()
            conexao.close()
            
            print(f"[SERVER LOG] Novo usuário cadastrado no banco: {nome_sanitizado} ({email_sanitizado})")
            return jsonify({"status": "sucesso", "mensagem": f"Cadastro de {nome_sanitizado} realizado com sucesso!"}), 201

        except sqlite3.IntegrityError:
            # Esse erro ocorre se o e-mail inserido já estiver na tabela (violando a restrição UNIQUE)
            return jsonify({"status": "erro", "mensagem": "Este e-mail já está cadastrado!"}), 400

    except Exception as e:
        print(f"[ERRO CRÍTICO NO CADASTRO]: {str(e)}")
        return jsonify({"status": "erro", "mensagem": "Ocorreu um erro interno ao processar o seu cadastro."}), 500

if __name__ == "__main__":
    # Mantive a porta 8000 que você já estava utilizando
    app.run(debug=False, port=8000)
