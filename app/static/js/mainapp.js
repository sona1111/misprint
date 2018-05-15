

$(document).ready(function(){

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/MISPrint');
    var previousImportant;
    var classSelectTopical = true;

    function printCompare(a,b) {
      if (a.name < b.name)
        return -1;
      else if (a.name > b.name)
        return 1;
      else
        return 0;
    }

    function isSamePrinterObjs(p1, p2){
        //console.log(p1);
        //console.log(p2);
        if(p1.length != p2.length){
            //console.log(p1.length);
            //console.log(p2.length);
            return false;
        }else{
            p1 = p1.sort(printCompare);
            p2 = p2.sort(printCompare);
            for(var i=0;i<p1.length;i++){

                //if(Object.keys(p1[i]).length != Object.keys(p2[i]).length){
                //    console.log(Object.keys(p1[i]).length);
                //    console.log(Object.keys(p2[i]).length);
                //    return false;
                //}
                var p1keys = Object.keys(p1[i]);
                for(var j=0;j<p1keys.length;j++){
                    if(p1[i][p1keys[j]] != p2[i][p1keys[j]]){
                        //console.log(p1[i][p1keys[j]]);
                        //console.log(p2[i][p1keys[j]]);
                        return false;
                    }
                }
            }
        }
        return true;
    }


    socket.on('connectConfirm', function(msg) {
        //console.log(msg);
    });

    socket.on('printerUpdate', function(msg) {

        //var msg = JSON.parse(msg);
        //console.log(msg);
        var fixedObj = {'printers':msg['data']};
        //console.log(isSamePrinterObjs(fixedObj['printers'], previousImportant['printers']));
        if(isSamePrinterObjs(fixedObj['printers'], previousImportant['printers'])){
            console.log("received I/O update with no changes");
        }else{

            $('#importantPrinterTable').parents().eq(2).css('background-color', '#000');
            setTimeout(function(){
                $('#importantPrinterTable').parents().eq(2).css('background-color', '');
            }, 500);
            writeImportantPrinterData({'printers':msg['data']});
            previousImportant = jQuery.extend(true, {}, fixedObj)
        }


    });


    function getColorByWarnLevel(level){
        if(level == 'low'){
            return '#F7FFB1';
        }else if(level == 'med'){
            return '#FFDCB1';
        }else{  //level == 'high'
            return '#FFB1B1';
        }
    }

    function writeImportantPrinterData(data){
        $('#importantPrinterTable').children().remove();
        for(var i=0; i<data['printers'].length;i++){
            if(!('tray2' in data['printers'][i])){
                data['printers'][i]['tray2'] = '';
            }
            var minutesLeft;

            if(data['printers'][i]['roomOpen']){
                minutesLeft = getMinutesleftFromDate(data['printers'][i]['roomOpen']) + ' minutes';
            }else{
                minutesLeft = 'N/A';
            }
            var row = '<tr data-ip={0}><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td></tr>';
            row = row.format(data['printers'][i]['ip'],
                             data['printers'][i]['room'],
                             data['printers'][i]['name'],
                             data['printers'][i]['panelMessage'],
                             data['printers'][i]['tonerPercent'],
                             data['printers'][i]['tray1'],
                             data['printers'][i]['tray2'],
                             minutesLeft);
            $('#importantPrinterTable').append(row);
            $('#importantPrinterTable tr:last-child').css('background-color', getColorByWarnLevel(data['printers'][i]['warnLevel']));
            $("#importantPrinterTable tr").click(function() {
                window.document.location = "http://" + $(this).attr("data-ip");
            });
        }
    }


    sendJS({}, 'getImportantPrinterData', function(r){
        //console.log(r);
        previousImportant = jQuery.extend(true, {}, r);
        writeImportantPrinterData(r);
    })


    function writePrinterData(data){
        for(var i=0; i<data['printers'].length;i++){
            if(!('error' in data['printers'][i])){
                if(!('tray2' in data['printers'][i])){
                    data['printers'][i]['tray2'] = '';
                }
                var row = '<tr data-ip={0}><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td></tr>';
                row = row.format(data['printers'][i]['ip'],
                                 data['printers'][i]['room'],
                                 data['printers'][i]['name'],
                                 data['printers'][i]['panelMessage'],
                                 data['printers'][i]['tonerPercent'],
                                 data['printers'][i]['tray1'],
                                 data['printers'][i]['tray2']);
                $('#printerTable').append(row);
            }else{
                var row = '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>';
                row = row.format(data['printers'][i]['room'],
                                 data['printers'][i]['name'],
                                 data['printers'][i]['error']);
                $('#printerErrorsTable').append(row);
                $('#printerErrorsTable').parent().show();
            }
            //$('#classroomTable tr:last-child').css('background-color', getColorByMinutes(minutesLeft));
            $("#printerTable tr").click(function() {
                window.document.location = "http://" + $(this).attr("data-ip");
            });
        }
    }

    setInterval(updatePrinterData, 300000);

    function updatePrinterData(){
        $('#printerTable').children().remove();
        $('#printerErrorsTable').children().remove();
        $('#printerErrorsTable').parent().hide();
        var room = $('#classroom2').val();
        var outObj = {};
        if(room){
            outObj['room'] = room;
        }
        sendJS(outObj, 'getPrinterData', function(r){
            writePrinterData(r);
        })
    }

    updatePrinterData();

    $('#printerSubmitBtn').click(updatePrinterData);




    function getColorByMinutes(minutes){
        if(minutes <= 15){
            return '#C4FFB1';
        }else if(minutes <= 30){
            return '#F7FFB1';
        }else if(minutes <= 60){
            return '#FFDCB1';
        }else{
            return '#FFB1B1';
        }
    }
    function getColorByMinutes_rev(minutes){
        if(minutes <= 15){
            return '#FFB1B1';
        }else if(minutes <= 30){
            return '#FFDCB1';
        }else if(minutes <= 60){
            return '#F7FFB1';
        }else{
            return '#C4FFB1';
        }
    }


    function getMinutesleftFromDate(dateStr){

        var d1 = new Date(dateStr);
        if(d1.dst()){
            d1.setHours(d1.getHours() + 4);
        }else{
            d1.setHours(d1.getHours() + 5);
        }
        var d2 = new Date();
        return DateDiff.inMinutes(d1, d2);
    }

    function writeClassData(data){
        if(classSelectTopical) {
            for (var i = 0; i < data['classes'].length; i++) {
                var row = '<tr><td>{0}</td><td>{1} minutes</td><td>{2}</td></tr>';
                var minutesLeft = getMinutesleftFromDate(data['classes'][i]['end']);
                row = row.format(data['classes'][i]['room'], minutesLeft, data['classes'][i]['title']);
                $('#classroomTable').append(row);
                $('#classroomTable tr:last-child').css('background-color', getColorByMinutes(minutesLeft));
            }
            for (var i = 0; i < data['classesBeginning'].length; i++) {
                var row = '<tr><td>{0}</td><td>{1} minutes</td><td>{2}</td></tr>';
                var minutesLeft = getMinutesleftFromDate(data['classesBeginning'][i]['start']);
                row = row.format(data['classesBeginning'][i]['room'], minutesLeft, data['classesBeginning'][i]['title']);
                $('#classroomBeginningTable').append(row);
                $('#classroomBeginningTable tr:last-child').css('background-color', getColorByMinutes_rev(minutesLeft));
            }
        }else{
            for (var i = 0; i < data['classes'].length; i++) {
                console.log(data['classes'][i]);
                // var row = '<tr><td>{0}</td><td>{1} minutes</td><td>{2}</td></tr>';
                // var minutesLeft = getMinutesleftFromDate(data['classes'][i]['end']);
                // row = row.format(data['classes'][i]['room'], minutesLeft, data['classes'][i]['title']);
                // $('#classroomTable').append(row);
                // $('#classroomTable tr:last-child').css('background-color', getColorByMinutes(minutesLeft));
            }
        }
    }

    setInterval(updateClassData, 300000);


    function updateClassData(){
        $('#classroomTable').children().remove();
        $('#classroomBeginningTable').children().remove();
        var room = $('#classroom').val();
        var outObj = {};
        if(room){
            outObj['room'] = room;
        }
        console.log(classSelectTopical);
        if(!classSelectTopical){
            outObj['start'] = $('#classCheckDateBegin').val();
            outObj['end'] = $('#classCheckDateEnd').val();
        }
        sendJS(outObj, 'getClassData', function(r){
            //console.log(r);
            writeClassData(r);
        })
    }
    updateClassData();

    $('#classSubmitBtn, #classSubmitBtn2').click(updateClassData);


    sendJS({}, 'getAllClassRooms', function(r){
        //console.log(r);
        for(var i=0; i<r['rooms'].length;i++){
            $('#classroom').append('<option>' + r['rooms'][i] + '</option>');
        }
    });

    sendJS({}, 'getAllPrinterRooms', function(r){
        //console.log(r);
        for(var i=0; i<r['rooms'].length;i++){
            $('#classroom2').append('<option>' + r['rooms'][i] + '</option>');
        }
    });

    $("#classroom").select2();
    $("#classroom2").select2();

    $("#classroom").change(function(){
        $('#classSubmitBtn').click();
    });
    $("#classroom2").change(function(){
        $('#printerSubmitBtn').click();
    });

    $('#refreshBeginBtn').click(function(){
       sendJS({}, 'refreshPrintersNow', function(){
           $('#refreshConfirm').show();
           $('#refreshBeginBtn').hide();
           $('#refreshConfirm').fadeOut(2500);
           setTimeout(function(){
               $('#refreshBeginBtn').show();
           }, 30000);

       })
    });


    $("#classCheck-switch").bootstrapSwitch();
    $("#classCheck-switch").on('switchChange.bootstrapSwitch', function(event, state) {
        if(state){
            classSelectTopical = true;
            $('#eventualClassCheckFrame, #eventualClassCheckPanels').fadeOut(100, function(){
                $('#topicalClassCheckFrame, #topicalClassCheckPanels').fadeIn();
            });
        }else{
            classSelectTopical = false;
            $('#topicalClassCheckFrame, #topicalClassCheckPanels').fadeOut(100, function(){
                $('#eventualClassCheckFrame, #eventualClassCheckPanels').fadeIn();
            });
        }
    });

    $('#classCheckDateBegin').Zebra_DatePicker();
    $('#classCheckDateEnd').Zebra_DatePicker();


});
