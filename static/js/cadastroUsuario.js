function cadastrarUsuario(){

    const matricula = $('input[name="matricula"]').val();
    const nome = $('input[name="nome"]').val();
    const senha = $('input[name="senha"]').val();
    const senha_confirmacao = $('input[name="senha_confirmacao"]').val();
    const cargo = $('input[name="cargo"]').val();
    
    if (senha !== senha_confirmacao)
    {
        alert("As senhas não coincidem!");
        return;
    }
    
    $.ajax({
        url: '/cadastrar',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({matricula, nome, senha, cargo}),
        sucess: function(response){
            alert(response.message);
        },
        error: function(xhr){
            console.error('Erro:', xhr.responseText);
        }
    });
}

function excluirUsuario(){
    const matricula = $('input[name="matricula"]').val();

    $.ajax({
        url: '/excluir',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ matricula }),
        sucess: function(response){
            alert(response.message)
        },
        error: function(xhr){
            console.error('Erro:',xhr.responseText);
        }
    });
}