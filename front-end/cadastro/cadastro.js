// Função global para remover/neutralizar caracteres perigosos (Proteção XSS)
function sanitizarTexto(texto) {
    const mapaCaracteres = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        "/": '&#x2F;'
    };
    // Substitui os caracteres especiais usando expressão regular
    return texto.replace(/[&<>"'/]/g, function(caractere) {
        return mapaCaracteres[caractere];
    });
}

// Aguarda o envio do formulário de cadastro
document.querySelector('#form-cadastro').addEventListener('submit', async function(event) {
    // Impede a página de recarregar antes de validarmos e enviarmos os dados
    event.preventDefault();

    // Captura e remove espaços em branco extras nas pontas (.trim())
    const nomeBruto = document.getElementById('nome').value.trim();
    const emailBruto = document.getElementById('email').value.trim();
    const senha = document.getElementById('senha').value;
    const confirmaSenha = document.getElementById('confirma-senha').value;

    // APLICA A SANITIZAÇÃO nos campos de texto textuais comuns
    const nomeSanitizado = sanitizarTexto(nomeBruto);
    const emailSanitizado = sanitizarTexto(emailBruto);
    // Nota de segurança: Não sanitizamos a senha para preservar caracteres complexos criados pelo usuário.
    // O HTTPS e a criptografia hash no Back-End cuidarão da proteção da senha.

    // 1. Validação local: Verifica se as duas senhas são idênticas
    if (senha !== confirmaSenha) {
        alert("Erro: As senhas digitadas não são iguais! Por favor, verifique.");
        return; // Interrompe a execução
    }

    // Criamos o pacote com os dados limpos e higienizados
    const dadosCadastro = {
        nome: nomeSanitizado,
        email: emailSanitizado,
        senha: senha
    };

    try {
        // O fetch envia os dados para o endpoint de cadastro no Python
        const resposta = await fetch('http://localhost:8000/cadastro', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosCadastro)
        });

        // Transforma a resposta do Python em objeto JavaScript
        const resultado = await resposta.json();

        if (resposta.ok) {
            // Se o Python respondeu com sucesso (código 201)
            alert(resultado.mensagem);
            window.location.href = "../login/login.html"; // Redireciona para a tela de login
        } else {
            // Se o Python retornou algum erro validado (Ex: e-mail já existe)
            // Lendo diretamente a chave 'mensagem' enviada pelo app.py
            alert("Erro no servidor: " + resultado.mensagem);
        }

    } catch (error) {
        console.error("Erro na comunicação:", error);
        alert("Não foi possível conectar ao servidor. Verifique se o Back-End está ligado!");
    }
});
