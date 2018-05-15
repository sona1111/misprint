

$(document).ready(function(){

    $('#termSubmitBtn').click(function(){
        $('#termSubmitStatus').text('!!! Updating, Please wait !!!');
        sendJS({'term':$('#termName').val()}, 'updateTermRun', function(r){
            if(r['ok']){
                $('#termSubmitStatus').text("Ok, the process completed without errors");
            }else{
                $('#termSubmitStatus').text(r['err']);
            }
        })
    })



});
