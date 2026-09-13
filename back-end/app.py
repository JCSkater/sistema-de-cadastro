from flask import Flask, request, jsonify
from flask_cors import CORS
import html  # Biblioteca nativa para sanitizar HTML/XSS
import re    # Biblioteca nativa para expressões regulares (Regex)

app = Flask(__name__)
CORS(app)

# Expressão regular para validar o formato do e-mail no servidor
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
# Expressão regular para validar o nome (apenas letras e espaços, de 3 a 50 caracteres)
NOME_REGEX = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]{3,50}$"

@app.route("/")
def home():
    return "Olá! O seu servidor Back-End em Python está funcionando localmente e protegido!"

# --- ENDPOINT DE LOGIN ---
@app.route("/login", methods=["POST"])
def login_endpoint():
    try:
        # Tenta capturar e decodificar os dados enviados
        dados = request.get_json()
        if not dados:
            return jsonify({"status": "erro", "mensagem": "Requisição inválida."}), 400
            
        email_bruto = dados.get("email", "").strip()
        senha = dados.get("senha")
        
        # 1. VALIDAÇÃO NO SERVIDOR: Garante que os campos existem
        if not email_bruto or not senha:
            return jsonify({"status": "erro", "mensagem": "E-mail e senha são obrigatórios!"}), 400
            
        # 2. SANITIZAÇÃO NO SERVIDOR: Neutraliza qualquer tentativa de XSS bypass
        email_sanitizado = html.escape(email_bruto)
        
        # 3. VALIDAÇÃO DE FORMATO: Checa se o e-mail é válido
        if not re.match(EMAIL_REGEX, email_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Formato de e-mail inválido!"}), 400

        # Validação fictícia de login (Substituiremos pelo Banco de Dados em breve)
        if email_sanitizado == "teste@email.com" and senha == "123456":
            return jsonify({"status": "sucesso", "mensagem": "Login autorizado!"}), 200
        else:
            return jsonify({"status": "erro", "mensagem": "E-mail ou senha incorretos."}), 401

    except Exception as e:
        # Se acontecer QUALQUER falha catastrófica inesperada (ex: JSON corrompido na rede)
        print(f"[ERRO CRÍTICO NO LOGIN]: {str(e)}")
        # Retorna um erro 500 controlado em formato JSON sem derrubar a aplicação
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

        # 3. VALIDAÇÃO DE REGEX: Força o padrão de segurança mesmo se burlarem o Front-End
        if not re.match(NOME_REGEX, nome_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Nome inválido! Use apenas letras e espaços."}), 400
            
        if not re.match(EMAIL_REGEX, email_sanitizado):
            return jsonify({"status": "erro", "mensagem": "Formato de e-mail inválido!"}), 400

        # Log seguro no terminal indicando o sucesso do recebimento higienizado
        print(f"[SERVER LOG] Novo usuário validado com sucesso: {nome_sanitizado} ({email_sanitizado})")

        return jsonify({"status": "sucesso", "mensagem": f"Cadastro de {nome_sanitizado} realizado com sucesso!"}), 201

    except Exception as e:
        # Captura falhas inesperadas no cadastro
        print(f"[ERRO CRÍTICO NO CADASTRO]: {str(e)}")
        return jsonify({"status": "erro", "mensagem": "Ocorreu um erro interno ao processar o seu cadastro."}), 500

if __name__ == "__main__":
    app.run(debug=False, port=8000)
