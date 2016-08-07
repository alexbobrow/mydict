$(function(){

    var currentProgressId = null;

    var csrf = getCookie('csrftoken');

    var ANSWERING = 0;
    var RESULT = 1;
    var PROCESSING = 3;

    var status = null;

	$(function(){


        $('input.test').on('keyup', function(e){
            var code = (e.charCode)? e.charCode : e.keyCode;
            if (status==RESULT && code==13) {
                $('input.test').val('');
                next();
                console.log('Enterok!');
            }
        });


        alexSuggest('input.test', {
            url: '/api/suggest',
            uniquePart: 'data-id',
            inputOffsetTop: 20,
            inputOffsetLeft: 0,
            inputOffsetWidth: 24,
            autoValueText: true, 
            onSelect: function(i, e){
                var id = e.attr('data-id');
                sendAnswer(id);
            },
            onPlainEnter: function(i){
                var o = i.data('alexSuggest');
                if ($('#alsuli' + " li").length==1) {
                    var id = $('#alsuli' + " li").attr('data-id');
                    sendAnswer(id);
                }

            }
        });


        next();

	});




    function next() {
        if (status==PROCESSING || status==ANSWERING) {
            return false;
        }
        status = PROCESSING;
        $('input.test').removeClass('wrong').removeClass('correct');
        $('.answer').fadeOut();
        $.get('/api/next', {}, function(ans){
            $('.word').text(ans.word);
            currentProgressId = ans.id;
            status = ANSWERING;
        }, 'json');
    }



    function sendAnswer(id) {

        status = PROCESSING;

        var data = {
            answer_id: id,
            progress_id: currentProgressId,
            csrfmiddlewaretoken: csrf,
        }

        $.post('/api/answer', data, function(ans){
            $('.answer').text(ans.answer).fadeIn();
            if (ans.correct) {
                $('input.test').addClass('correct');
            } else {
                $('input.test').addClass('wrong');
            }
            status = RESULT;
        }, 'json');


    }



});




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