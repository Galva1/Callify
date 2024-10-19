$(document).ready(function(){
    $('button[name="salvar"]').click(function(){
        $('.menu-secundario-top input').val('');
        $('.menu-secundario-bot input').val('');
    });
});

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
            showMessage(response.message, 'success');
            $('input').val('');
        },
        error: function(response){
            var errorMessage = response.responseJSON ? response.responseJSON.message : "Ocorreu um erro.";
            showMessage(errorMessage, 'danger');
        }
    });
}

function showMessage(message, type) {
    const alertBox = $('<div>').addClass(`alert alert-${type}`).text(message);
    $('.menu-secundario-bot').append(alertBox);

    setTimeout(() => {
        alertBox.fadeOut(400, function() { $(this).remove(); });
    }, 3000);
}

function excluirUsuario(){
    const matricula = $('input[name="matricula"]').val();

    $.ajax({
        url: '/excluir',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ matricula }),
        sucess: function(response){
            alert(response.message);
            $('input').val('');
        },
        error: function(xhr){
            console.error('Erro:',xhr.responseText);
        }
    });
}