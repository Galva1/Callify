$(document).ready(function(){
    $('input[name="chamado"]').change(function(){
        if($(this).val() === 'sim'){
            $('#matriculaDiv').addClass('hidden');
        } else {
            $('#matriculaDiv').removeClass('hidden');
        }
    });
});