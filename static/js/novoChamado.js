$(document).ready(function(){
    $('input[name="chamado"]').change(function(){
        if($(this).val() === 'sim'){
            $('#matriculaDiv').addClass('hidden');
            $('#matriculaDiv input').val('');
        } else {
            $('#matriculaDiv').removeClass('hidden');
        }
    });
});