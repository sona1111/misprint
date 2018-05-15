

//function to clone an object.
function clone(obj){
    if(obj == null || typeof(obj) != 'object')
        return obj;

    var temp = obj.constructor(); // changed

    for(var key in obj)
        temp[key] = clone(obj[key]);
    return temp;
}


//general function for ajax call that works correctly with flask.
function sendJS(obj, path, callback){

    $.ajax({
        type: "POST",
        url: 'http://' + document.domain + ':' + location.port + '/' + path,
        data: JSON.stringify(obj),
        success: callback,
        dataType: 'json',
        contentType:"application/json"
    });

}

function isInArray(value, array) {
        return array.indexOf(value) > -1;
}

if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

$.fn.enterKey = function (fnc) {
    return this.each(function () {
        $(this).keypress(function (ev) {
            var keycode = (ev.keyCode ? ev.keyCode : ev.which);
            if (keycode == '13') {
                fnc.call(this, ev);
            }
        })
    })
}

jQuery.expr.filters.offscreen = function(el) {
  return (
              (el.offsetLeft + el.offsetWidth) < 0
              || (el.offsetTop + el.offsetHeight) < 0
              || (el.offsetLeft > window.innerWidth || el.offsetTop > window.innerHeight)
         );
};

function isScrolledIntoView(elem)
{
    var $elem = $(elem);
    var $window = $(window);

    var docViewTop = $window.scrollTop();
    var docViewBottom = docViewTop + $window.height();

    var elemTop = $elem.offset().top;
    var elemBottom = elemTop + $elem.height();

    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
}

var DateDiff = {

    inMinutes: function(d1, d2) {
        var t2 = d2.getTime();
        var t1 = d1.getTime();

        //var hours = parseInt((t2-t1)/(3600*1000));
        return parseInt((t1-t2)/(60*1000));

    },

    inDays: function(d1, d2) {
        var t2 = d2.getTime();
        var t1 = d1.getTime();

        return parseInt((t2-t1)/(24*3600*1000));
    },

    inWeeks: function(d1, d2) {
        var t2 = d2.getTime();
        var t1 = d1.getTime();

        return parseInt((t2-t1)/(24*3600*1000*7));
    },

    inMonths: function(d1, d2) {
        var d1Y = d1.getFullYear();
        var d2Y = d2.getFullYear();
        var d1M = d1.getMonth();
        var d2M = d2.getMonth();

        return (d2M+12*d2Y)-(d1M+12*d1Y);
    },

    inYears: function(d1, d2) {
        return d2.getFullYear()-d1.getFullYear();
    }
}

Date.prototype.stdTimezoneOffset = function() {
    var jan = new Date(this.getFullYear(), 0, 1);
    var jul = new Date(this.getFullYear(), 6, 1);
    return Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset());
}

Date.prototype.dst = function() {
    return this.getTimezoneOffset() < this.stdTimezoneOffset();
}

document.head = document.head || document.getElementsByTagName('head')[0];

function changeFavicon(src) {
 var link = document.createElement('link'),
     oldLink = document.getElementById('dynamic-favicon');
 link.id = 'dynamic-favicon';
 link.rel = 'shortcut icon';
 link.href = src;
 if (oldLink) {
  document.head.removeChild(oldLink);
 }
 document.head.appendChild(link);
}

function getFmtTime(){
    var date = new Date();
    var time = ('0'  + date.getMinutes()).slice(-2)+':'+('0' + date.getSeconds()).slice(-2);
    var out = "{0}/{1}~{2}:{3}".format(date.getMonth() + 1,
                                           date.getDay() + 1,
                                           date.getHours(),
                                           time);
    return out;
}