function buscarChamado(){
    const operador = $('input[name="operador"]').val();
    const start_date = $('input[name="start_date"]').val();
    const end_date = $('input[name="end_date"]').val();
    const situacao = $('input[name="situacao"]').val();
    const protocolo = $('input[name="protocolo"]').val();

    $.ajax({
        url: '/buscar',
        method: 'GET',
        data: {operador:operador, start_date:start_date, end_date:end_date, situacao:situacao, protocolo:protocolo},
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.error('Erro:', error);
        }
    });

}