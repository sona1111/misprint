$(document).ready(function(){

    var kode = []
    var needed = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65, 13];

    function updateKode(newKey){
        if(needed[kode.length] == newKey){
            kode.push(newKey)
            if(kode.length == needed.length){
                //console.log('complete');
                //initiate browser ponies
                kode = [];
            }
        }else{
            kode = [];
        }
    }

    $(document).keydown(function(e) {
        updateKode(e.which);

    });


});

