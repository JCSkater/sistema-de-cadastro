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
    return texto.replace(/[&<>"'/]/g, function(caractere) {
        return mapaCaracteres[caractere];
    });
}

// Aguarda o envio do formulário de login
// Nota: Certifique-se de que seu <form> no HTML possua o id="form-login" ou ajuste o seletor abaixo
document.querySelector('form').addEventListener('submit', async function(event) {
    // Impede a página de recarregar antes de enviarmos os dados
    event.preventDefault();

    // Captura e remove espaços em branco extras nas pontas (.trim())
    const emailBruto = document.getElementById('email').value.trim();
    const senha = document.getElementById('senha').value;

    // APLICA A SANITIZAÇÃO no campo de e-mail
    const emailSanitizado = sanitizarTexto(emailBruto);
    // A senha não é sanitizada para preservar caracteres complexos criados pelo usuário

    // Criamos o pacote com os dados exatos que o app.py espera receber
    const dadosLogin = {
        email: emailSanitizado,
        senha: senha
    };

    try {
        // O fetch envia os dados para o endpoint de login no Python
        const resposta = await fetch('https://sistema-de-cadastro-iuj1.onrender.com/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosLogin)
        });

        // Transforma a resposta do Python em objeto JavaScript
        const resultado = await resposta.json();

        if (resposta.ok) {
            // Se o Python respondeu com sucesso (código 200 - Login autorizado!)
            alert(resultado.mensagem);
            
            // Aqui você pode redirecionar o usuário para a página principal do seu sistema pós-login
            // window.location.href = "dashboard.html"; 
        } else {
            // Se o Python retornou erro (código 401 - Incorreto ou 400 - Inválido)
            alert("Erro ao entrar: " + resultado.mensagem);
        }

    } catch (error) {
        console.error("Erro na comunicação:", error);
        alert("Não foi possível conectar ao servidor. Verifique se o servidor está ligado!");
    }
});
