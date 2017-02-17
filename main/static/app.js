$(function(){

    // vars

    var csrf = getCookie('csrftoken');

    var aud = $('audio')[0];

    var wordId = null;

    var log = [];

    var logPosition = 0;

    // initialization




    // binds

    $(window).on('keyup', function(e){
        var code = (e.charCode)? e.charCode : e.keyCode;
        if (code==13) {
            next();
        }
        if (code==8) {
            prev();
        }
    });


    $('button[data-action=disable]').on('click', function(e){
        if (!confirm('Отключить это слово?')) {
            return false;
        }
        var data = {
            progress_id: currentProgressId,
            csrfmiddlewaretoken: csrf,
        }
        $.post(appUrls.disable, data, function(ans){
            next();
        }, 'json');            
    });


    
    $('button[data-action=report]').on('click', function(e){
        if (!confirm('Сообщить о проблеме с этим словом?')) {
            return false;
        }

        var message = prompt('Комментарий: (необязательно)');

        var data = {
            csrfmiddlewaretoken: csrf,
            message: message
        }

        data['word_id'] = lwordId;

        $.post(appUrls.report, data, function(ans){
            alert('Спасибо, Ваше сообщение отправлено');
        }, 'json');

    });




    $('span.word').on('click', function(e){
        replay();
        e.stopPropagation();
    });


    
    $('body').on('click', function(e){
        next();
    });



    // private functions

    function replay() {
        if (aud.src!='') {
            aud.play();
        }
    }


    function prev() {
        console.log('prev');
        var newPos = logPosition-1;
        console.log('newPos', newPos);
        var id = log.length + newPos-1;
        console.log('id', id);
        if (id < log.length && id >= 0) {
            var ans = log[id];
            setWord(ans);
            logPosition--;
        }     
        
    }


    function next() {


        if (logPosition<0) {
            console.log('log pos < 0');
            var id = log.length + logPosition;
            console.log('id', id);
            var ans = log[id];
            setWord(ans);
            logPosition++;
            return
        }

        $.get(appUrls.next, {}, function(ans){
            log.push(ans);
            if (log.length>5) {
                log.shift();
            };
            console.log(log);
            setWord(ans);
        }, 'json');

    }

    function setWord(ans) {
        wordId = ans.id;
        $('span.word').text(ans.word);
        setFontSize(ans.translation);
        $('.answer').text(ans.translation);
        $('input.test').focus();
        aud.src = ans.pronounce;
    }



    function setFontSize(str) {
        var len = str.length;
        var sizeClass = 's1';
        if (len>20) { 
            sizeClass = 's2';
        }
        if (len>30) {
            sizeClass = 's3';
        }
        if (len>40) {
            sizeClass = 's4';
        }
        $('.answer').attr('class', 'answer ' + sizeClass);
    }

    next();


}); // dom ready




function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}