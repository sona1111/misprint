$(document).ready(function(){

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/MISChat',
                            {} );
    var room = 'LOCAL';
    var status = 'online';
    var chatrooms = [];
    var chatRoomsIdle = {};
    var onlineUsers = [];
    var onlineUsersNames = {};
    var awayUsers = [];
    var awayUsersNames = {};

    var alertSounds = true;
    var alertText = true;

    socket.emit('connect');
    socket.on('connectConfirm', function(msg) {
        //room = msg['room'];
        socket.emit('joined', user, 'staff', room, fName, lName, getFmtTime());
    });

    window.onbeforeunload = function() {
        socket.emit('userDisconnect', user, room, fName, lName, getFmtTime());
    }


    var openRooms = [];

    
    

    var chatBoxHTML =
        '<div class="col-md-6 chatbox" data-chatroom="{0}">' +
            '<div class="panel panel-danger">' +
                '<div class="panel-heading">Chat with {1} {2} ({3}) @ {0}' +
                '<button type="button" class="close" data-target="[data-chatroom=\'{0}\']" data-dismiss="alert">' +
                '<span aria-hidden="true">&times;</span></button></div>' +
                '<div class="panel-body">' +
                    '<div class="form-group">' +
                      '<textarea disabled class="form-control textoutput" rows="12"></textarea>' +
                        '<input class="form-control chatmsginput">' +
                        '<button type="button" class="btn btn-default chatsendbtn">Send</button>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';

    $("#status-switch").bootstrapSwitch();
    $("#status-switch").on('switchChange.bootstrapSwitch', function(event, state) {
        if(state){
            status = 'online';
        }else{
            status = 'away';
        }
        socket.emit('changedStatus', user, status);
    });
    socket.on('changedStatus', function(msg) {
        if(msg['status'] == 'away' && isInArray(msg['user'], onlineUsers)){
            var index = onlineUsers.indexOf(msg['user']);
            onlineUsers.splice(index, 1);
            awayUsers.push(msg['user']);
            awayUsersNames[msg['user']] = onlineUsersNames[msg['user']];
            delete onlineUsersNames[msg['user']];
        }else if(msg['status'] == 'online' && isInArray(msg['user'], awayUsers)){
            var index = awayUsers.indexOf(msg['user']);
            awayUsers.splice(index, 1);
            onlineUsers.push(msg['user']);
            onlineUsersNames[msg['user']] = awayUsersNames[msg['user']];
            delete awayUsersNames[msg['user']];
        }
        updateUsersStatus();
    });

    socket.on('checkUsersOnlineInit', function(msg) {
        socket.emit('checkUsersOnlineConfirm', user, 'staff', status, fName, lName, getFmtTime());
    });

    socket.emit('checkUsersOnlineInit');
    socket.on('checkUsersOnlineConfirm', function(msg) {
        if(msg['mode'] == 'staff'){
            if(msg['status'] == 'online' && !isInArray(msg['user'], onlineUsers)){
                onlineUsers.push(msg['user']);
                onlineUsersNames[msg['user']] = "{0} {1}".format(msg['fname'], msg['lname']);
            }else if(msg['status'] == 'away' && !isInArray(msg['user'], awayUsers)){
                awayUsers.push(msg['user']);
                awayUsersNames[msg['user']] = "{0} {1}".format(msg['fname'], msg['lname']);
            }
        }else if(msg['mode'] == 'client'){
            setupChatBox(msg['room'], msg['fname'], msg['lname'], msg['user']);
            var chatBox = $('.chatbox[data-chatroom="{0}"] .textoutput'.format(msg['room']));

            for(var i=0;i<msg['msgs'].length;i++){
                if('joined' in msg['msgs'][i]){
                    chatBox.append("[{0}] {1} {2} ({3}) Has joined the room\n".format(msg['msgs'][i]['time'], msg['msgs'][i]['fname'], msg['msgs'][i]['lname'], msg['msgs'][i]['user']));
                }else if('left' in msg['msgs'][i]){
                    chatBox.append("[{0}] {1} {2} ({3}) Has left the room\n".format(msg['msgs'][i]['time'], msg['msgs'][i]['fname'], msg['msgs'][i]['lname'], msg['msgs'][i]['user']));
                }else{
                    chatBox.append("[{0}] {1} {2}: {3}\n".format(msg['msgs'][i]['time'], msg['msgs'][i]['fname'], msg['msgs'][i]['lname'], msg['msgs'][i]['msg']));
                }
                chatBox[0].scrollTop = chatBox[0].scrollHeight;
            }
        }
        updateUsersStatus();
    });

    function updateUsersStatus(){
        $('#numUsersOnline').val(onlineUsers.length);
        $('#numUsersAway').val(awayUsers.length);
        $('#numUsersOnline2').html('');
        for(var i = 0;i<onlineUsers.length; i++){
            $('#numUsersOnline2').append('<li class="list-group-item">{0}</li>'.format(onlineUsersNames[onlineUsers[i]]));
        }
    }


    socket.on('joined', function(msg) {
        if(msg['mode'] == 'client'){
            setupChatBox(msg['room'], msg['fname'], msg['lname'], msg['user']);
//            $('.chatbox[data-chatroom="{0}"] button'.format(msg['room'])).click(function(){
//                var data = $(this).parent().find('input').val();
//                socket.emit('chatMsg', user, data, msg['room']);
//                $(this).parent().find('input').val('');
//            })
        }
        var chatBox = $('.chatbox[data-chatroom="{0}"] .textoutput'.format(msg['room']));
        chatBox.append("[{0}] {1} {2} ({3}) Has joined the room\n".format(msg['time'], msg['fname'], msg['lname'], msg['user']));
        chatBox[0].scrollTop = chatBox[0].scrollHeight;
    });

    socket.on('userDisconnect', function(msg) {
        removeChatBox(msg['room']);
        var chatBox = $('.chatbox[data-chatroom="{0}"] .textoutput'.format(msg['room']));
        chatBox.append("{0} {1} ({2}) Has left the room\n".format(msg['fname'], msg['lname'], msg['user']));
        chatBox[0].scrollTop = chatBox[0].scrollHeight;
    });

    socket.on('chatMsg', function(msg){
        //console.log('received chatmsg from chatbox {0}'.format(msg['room']));
        var chatBox = $('.chatbox[data-chatroom="{0}"] .textoutput'.format(msg['room']));
        if(chatBox){
            clearInterval(alertInterval);
            clearInterval(alertSoundInterval);
            chatBox.append("[{0}] {1} {2}: {3}\n".format(msg['time'], msg['fname'], msg['lname'], msg['data']));
            chatBox[0].scrollTop = chatBox[0].scrollHeight;
            if(!(msg['room'] == 'LOCAL')){
                if(msg['room'] in chatRoomsIdle){
                    var secondsPassed = (Date.now() -  chatRoomsIdle[msg['room']])/ 1000;
                    if(secondsPassed > 30){
                        alertChat(msg['room']);
                        runSoundInterval();
                    }else{

                    }
                }else{
                    alertChat(msg['room']);
                    runSoundInterval();
                }
            }
        }else{
            console.log("Message Received for non-existent chatbox {0}".format(msg['room']))
        }
    });

    function playAlertSound(){
        document.getElementById('alertSound').pause();
        document.getElementById('alertSound').currentTime = 0;
        document.getElementById('alertSound').play();
    }

    $(window).on("keypress", function(){
        clearInterval(alertSoundInterval);
    });

    var hasFocus = true;
    $(window).on("blur focus", function(e) {
        var prevType = $(this).data("prevType");

        if (prevType != e.type) {   //  reduce double fire issues
            switch (e.type) {
                case "blur":
                    hasFocus = false;
                    break;
                case "focus":
                    hasFocus = true;
                    break;
            }
        }
        $(this).data("prevType", e.type);
    });

    var textAlertState = false;
    var originalDoctitle = document.title;
    var alertInterval = null;
    var alertSoundInterval = null;
    function runAlertInterval(){
        clearInterval(alertInterval);
        alertInterval = setInterval(function(){
            if(hasFocus){
                clearInterval(alertInterval);
                document.title = originalDoctitle;
                changeFavicon(defaultFaviconSrc);
            }else{
                if(alertText){
                    if (textAlertState) {
                        document.title = "!!!~~New Alert~~!!!";
                        changeFavicon(alertFaviconSrc);
                    } else {
                        document.title = originalDoctitle;
                        changeFavicon(defaultFaviconSrc);
                    }
                    textAlertState = !textAlertState;
                }
            }

        }, 1000);

    }

    function runSoundInterval(){
        clearInterval(alertSoundInterval);
        alertSoundInterval = setInterval(function(){
            playAlertSound();
        }, 3000);
    }

    function alertChat(room){
        runAlertInterval();
        var chatbox = $('.chatbox[data-chatroom="{0}"] .panel-body'.format(room));
        chatbox.css('background-color', '#000');
        $('.jumbotron').css('background-color', '#FFA500');
        setTimeout(function(){
            chatbox.css('background-color', '');

        }, 500);
        setTimeout(function(){
            chatbox.css('background-color', '#000');
        }, 1000);
        setTimeout(function(){
            chatbox.css('background-color', '');
            $('.jumbotron').css('background-color', '');
        }, 1500);
    }

//
//    socket.on('joined', function(msg) {
//        console.log(msg);
//        if(msg['mode'] == 'client' && msg['room'] == room && msg['user'] == user){
//            console.log("client has joined! room {0} (self) user {1}".format(msg['room'], msg['user']));
//            setupChatBoxEvents($('#chatbox'));
//        }
//    });

    function setupChatBox(room, fname, lname, user){
        if(!isInArray(room, chatrooms)){
            chatrooms.push(room);
            console.log("setting up chat box: room {0} user {1}".format(room, user));
            var chatBox = chatBoxHTML.format(room, fname, lname, user);
            $('#chatBoxesContainer').append(chatBox);
            setupChatBoxEvents($('.chatbox[data-chatroom="{0}"]'.format(room)));
        }
    };

    function removeChatBox(room){
        if(isInArray(room, chatrooms)){
            var index = chatrooms.indexOf(room);
            chatrooms.splice(index, 1);
            var chatbox = $('.chatbox[data-chatroom="{0}"]'.format(room));
            chatbox.find('.panel-danger').addClass('panel-default').removeClass('panel-danger');
            chatbox.find('.chatmsginput').prop('disabled', true);
            chatbox.find('.chatsendbtn').prop('disabled', true);
            chatbox.find('.close').show();
        }
    }

    function setupChatBoxEvents(chatbox){
        var button = chatbox.find('.chatsendbtn');
        button.unbind();
        button.click(function(){
            sendChatMsgHandler(chatbox);
        });
        var inputline = chatbox.find('.chatmsginput');
        inputline.unbind();
        inputline.keypress(function(e){
            if(e.which == 13) {
                e.preventDefault();
                sendChatMsgHandler(chatbox);
            }
        });
    }

    function sendChatMsgHandler(chatbox){
        var data = chatbox.find('.chatmsginput').val();
        var room = chatbox.attr('data-chatroom');
        socket.emit('chatMsg', user, fName, lName, data, room, getFmtTime());
        chatbox.find('.chatmsginput').val('');
        chatRoomsIdle[room] = Date.now();
    }

    setupChatBoxEvents($('.chatbox[data-chatroom="{0}"]'.format('LOCAL')));

        var chatBox = $('.chatbox[data-chatroom="{0}"] .textoutput'.format('LOCAL'));
        sendJS({}, 'getlocalmsgs', function(msg){
            for(var i=0;i<msg['msgs'].length;i++){
                if('joined' in msg['msgs'][i]){
                    chatBox.append("[{0}] {1} {2} ({3}) Has joined the room\n".format(msg['msgs'][i]['time'], msg['msgs'][i]['fname'], msg['msgs'][i]['lname'], msg['msgs'][i]['user']));
                }else if('left' in msg['msgs'][i]){
                    chatBox.append("[{0}] {1} {2} ({3}) Has left the room\n".format(msg['msgs'][i]['time'], msg['msgs'][i]['fname'], msg['msgs'][i]['lname'], msg['msgs'][i]['user']));
                }else{
                    chatBox.append("[{0}] {1} {2}: {3}\n".format(msg['msgs'][i]['time'], msg['msgs'][i]['fname'], msg['msgs'][i]['lname'], msg['msgs'][i]['msg']));
                }
                chatBox[0].scrollTop = chatBox[0].scrollHeight;
            }
        })

    changeFavicon(defaultFaviconSrc);
});

