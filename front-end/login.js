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

// Aguarda o usuário enviar o formulário de login
document.querySelector('#form-login').addEventListener('submit', async function(event) {
    // Impede a página de recarregar imediatamente
    event.preventDefault();

    // Captura e remove espaços extras
    const emailBruto = document.getElementById('email').value.trim();
    const senha = document.getElementById('senha').value;

    // APLICA A SANITIZAÇÃO
    const emailSanitizado = sanitizarTexto(emailBruto);

    // Criamos o pacotinho de dados higienizado
    const dadosFormulario = {
        email: emailSanitizado,
        senha: senha
    };

    try {
        // O fetch faz o papel de enviar os dados para o endpoint do Python
        const resposta = await fetch('http://localhost:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosFormulario)
        });

        // Transforma a resposta que veio do Python em um objeto JavaScript
        const resultado = await resposta.json();

        // Se o servidor Python respondeu com sucesso (código 200)
        if (resposta.ok) {
            alert(resultado.mensagem); // "Login autorizado!"
            window.location.href = "index.html"; // Redireciona
        } else {
            // Se o servidor Python recusou (código 401 ou outros)
            alert("Erro: " + resultado.mensagem); // "E-mail ou senha incorretos."
        }

    } catch (error) {
        console.error("Erro na comunicação:", error);
        alert("Não foi possível conectar ao servidor. Verifique se o Back-End está ligado!");
    }
});
