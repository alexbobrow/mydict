$(function(){

    // vars

    var currentProgressId = null;

    var csrf = getCookie('csrftoken');

    var aud = $('audio')[0];

    var ANSWERING = 0;
    var RESULT = 1;
    var CORRECT = 2;
    var PROCESSING = 3;

    var status = null;

    var debug = window.localStorage.getItem('debug');

    var lastResult = null;


    // initialization



    alexSuggest('input.test', {
        url: appUrls.suggest,
        uniquePart: 'data-id',
        inputOffsetTop: 20,
        inputOffsetLeft: 0,
        inputOffsetWidth: 24,
        autoValueText: true, 
        onSelect: function(i, e){
            var id = e.attr('data-id');
            sendAnswer(id, false);
        },
        onPlainEnter: function(i){
            //var o = i.data('alexSuggest');
            sendAnswer(i.val(), true);
        }
    });    


    // show debug if needed
    if (debug==='true') {
        $('table.debug').show();
    }


    // binds

    $(window).on('keyup', function(e){
        var code = (e.charCode)? e.charCode : e.keyCode;
        if ((status==RESULT || status==CORRECT) && code==13) {
            $('input.test').val('');
            nextOrCorrect();
        }
    });


    $('input.test').on('keyup', function(e){
        var code = (e.charCode)? e.charCode : e.keyCode;
        if ((status==RESULT || status==CORRECT) && code==13) {
            $('input.test').val('');
            nextOrCorrect();
            e.stopPropagation();
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
            status = null;
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

        if (status==CORRECT) {
            data['word_id'] = lastResult.answerWordId;
        } else {
            data['progress_id'] = currentProgressId;
        }


        $.post(appUrls.report, data, function(ans){
            alert('Спасибо, Ваше сообщение отправлено');
        }, 'json');

    });



    $('div.word').on('click', function(e){
        replay();
    });


    $('a[data-action=toggle-debug]').on('click', function(e){
        e.preventDefault();
        if ($('table.debug').is(':visible')) {
            $('table.debug').hide();
            window.localStorage.setItem('debug', 'false');
        } else {
            $('table.debug').show();
            window.localStorage.setItem('debug', 'true');
        }
    });



    // private functions


    function replay() {
        if (aud.src!='') {
            aud.play();
        }
    }




    function nextOrCorrect() {
        // if answer was wrong, show reverse translation of
        // wrong answer
        if (status==RESULT && (lastResult.userWord)) {
            status=CORRECT;
            $('span.word').text(lastResult.userWord.word);
            $('.answer').text(lastResult.userWord.translation);
            return;
        }
        next();
    }






    function next() {
        if (status==PROCESSING || status==ANSWERING) {
            return false;
        }
        status = PROCESSING;
        $('input.test').removeClass('wrong').removeClass('correct');
        $('.answer').fadeOut();
        $.get(appUrls.next, {}, function(ans){
            $('span.word').text(ans.word);
            $('input.test').focus();

            aud.src = ans.pronounce;

            if ($('table.debug').length>0) {
                $('table.debug').empty();
                $.each(ans.debug, function(k, v){
                    if (typeof(v)=='object') {
                        $('table.debug').append("<tr><td>"+v.key+"</td><td>"+v.value+"</td></tr>");
                    } else {
                        $('table.debug').append("<tr><td colspan='2'>"+v+"</td></tr>");
                    }                   
                });
            }

            currentProgressId = ans.id;
            status = ANSWERING;
        }, 'json');
    }




    //function sendAnswer(id, is_text) {
    function sendAnswer(answer, is_text) {

        status = PROCESSING;

        var data = {
            progress_id: currentProgressId,
            csrfmiddlewaretoken: csrf,
        }

        if (is_text) {
            data['answer_text'] = answer;
        } else {
            data['answer_id'] = answer;
        }


        $.post(appUrls.answer, data, function(ans){
            lastResult = ans;
            $('.answer').text(ans.correctWord.translation).fadeIn();
            if (ans.success) {
                $('input.test').addClass('correct');
            } else {
                $('input.test').addClass('wrong');
            }
            status = RESULT;
        }, 'json');
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