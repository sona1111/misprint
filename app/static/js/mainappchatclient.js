$(document).ready(function(){

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/MISChat', {});
    var room = null;
    var onlineUsers = [];
    var awayUsers = [];

    socket.emit('connect');
    socket.on('connectConfirm', function(msg) {
        room = msg['room'];
        if(roomName){
            room = roomName + "-" + room;
        }


        socket.emit('joined', user, 'client', room, fName, lName, getFmtTime());
    });

    window.onbeforeunload = function() {
        socket.emit('userDisconnect', user, room, fName, lName, getFmtTime());
    }

    socket.on('joined', function(msg) {
        if(msg['mode'] == 'client' && msg['room'] == room && msg['user'] == user){
            console.log("client has joined! room {0} (self) user {1}".format(msg['room'], msg['user']));
            setupChatBoxEvents($('#chatbox'));
        }
    });

    socket.on('chatMsg', function(msg){
        if(msg['room'] == room){
            var chatBox = $('#chatbox .textoutput');
            if(chatBox){
                chatBox.append("{0} {1}: {2}\n".format(msg['fname'], msg['lname'], msg['data']));
                chatBox[0].scrollTop = chatBox[0].scrollHeight;
            }else{
                console.log("Message Received for non-existent chatbox {0}".format(msg['room']))
            }
        }
    })

    socket.on('changedStatus', function(msg) {
        if(msg['status'] == 'away' && isInArray(msg['user'], onlineUsers)){
            var index = onlineUsers.indexOf(msg['user']);
            onlineUsers.splice(index, 1);
            awayUsers.push(msg['user']);
        }else if(msg['status'] == 'online' && isInArray(msg['user'], awayUsers)){
            var index = awayUsers.indexOf(msg['user']);
            awayUsers.splice(index, 1);
            onlineUsers.push(msg['user']);
        }
        updateUsersStatus();
    });

    socket.on('checkUsersOnlineInit', function(msg) {
        socket.emit('checkUsersOnlineConfirm', user, 'client', room, fName, lName, getFmtTime());
    });

    socket.emit('checkUsersOnlineInit');
    socket.on('checkUsersOnlineConfirm', function(msg) {
        if(msg['mode'] == 'staff'){
            if(msg['status'] == 'online' && !isInArray(msg['user'], onlineUsers)){
                onlineUsers.push(msg['user']);
            }else if(msg['status'] == 'away' && !isInArray(msg['user'], awayUsers)){
                awayUsers.push(msg['user']);
            }
        }
        updateUsersStatus();
    });

    function updateUsersStatus(){
        $('.statusmsg').text('{0} agents online ; {1} agents away'.format(onlineUsers.length, awayUsers.length));
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
        socket.emit('chatMsg', user, fName, lName, data, room, getFmtTime());
        chatbox.find('.chatmsginput').val('');
    }

});

