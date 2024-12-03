function abrirDisplay(){  
    const interfaceSelecionada = $('section[name="interface"]');

    interfaceSelecionada.toggle();
    $('.d-card').show();
}

function fecharDisplay(){
    const interfaceSelecionada = $('section[name="interface"]');
    location.reload();
    interfaceSelecionada.toggle();
    $('.d-card').hide();
    
}

function buscarInformacoes(card){
    const $card= $(card).closest('.cardInterface');
    const idchamado = $card.data('idchamado');
    const titulo = $card.data('titulo');
    const descricao = $card.data('descricao');
    const responsavel = $card.data('responsavel');
    const operador = $card.data('operador');
    const urgencia = $card.data('urgencia');
    const observacao = $card.data('observacao');
    const criado = $card.data('criado');
    const status = $card.data('status');

    $('#titulo').val(titulo);
    $('#descricao').val(descricao);
    $('#status').text(status);
    $('#responsavel').text(responsavel);
    $('#status').text(status);
    $('#observacao').text(observacao);
    $('#urgencia').text(urgencia);
    $('#idchamado').text(idchamado);
}

function pegarChamado(){
    const idchamado = $('p[name="idchamado"]').text();
    const matricula = $('p[name="idchamado"]').data('matricula');
    $.ajax({
        url: '/pegarChamado',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({idchamado, matricula}),
        sucess: function(response){
            showMessage(response.message, 'success');
        },
        error: function(response){
            var errorMessage = response.responseJSON ? response.responseJSON.message : "Ocorreu um erro.";
            showMessage(errorMessage, 'danger');
        }
    });
}

function soltarChamado(){
    const idchamado = $('p[name="idchamado"]').text();
    const matricula = $('p[name="idchamado"]').data('matricula');
    $.ajax({
        url: '/soltarChamado',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({idchamado, matricula}),
        sucess: function(response){
            showMessage(response.message, 'success');
        },
        error: function(response){
            var errorMessage = response.responseJSON ? response.responseJSON.message : "Ocorreu um erro.";
            showMessage(errorMessage, 'danger');
        }
    });
}

function finalizarChamado(){
    const idchamado = $('p[name="idchamado"]').text();
    const matricula = $('p[name="idchamado"]').data('matricula');
    $.ajax({
        url: '/finalizarChamado',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({idchamado, matricula}),
        sucess: function(response){
            showMessage(response.message, 'success');
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