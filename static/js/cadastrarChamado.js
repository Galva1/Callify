function cadastrarChamado(){
    const titulo = $('input[name="titulo"]').val();
    const descricao = $('input[name="descricao"]').val();
    const matricula = $('input[name="matricula"]').val();
    const chamado = $('input[name="chamado"]:checked').val();

    $.ajax({
        url: '/cadastrarChamado',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({titulo, descricao, matricula, chamado}),
        sucess: function(response){
            alert(response.message);
        },
        error: function(xhr){
            console.error('Erro:', xhr.responseText);
        }
    });
}

