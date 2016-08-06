$(function(){



	$(function(){

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
        });


        next();

	});

    var currentProgressId = null;

    var csrf = getCookie('csrftoken');


    function next() {
        $.get('/api/next', {}, function(ans){
            $('.word').text(ans.word);
            currentProgressId = ans.id;
        }, 'json');
    }



    function sendAnswer(id) {

        var data = {
            answer_id: id,
            progress_id: currentProgressId,
            csrfmiddlewaretoken: csrf,
        }

        $.post('/api/answer', data, function(ans){
            $('.answer').text(ans.answer);
            if (ans.correct) {
                $('input.test').addClass('correct');
            } else {
                $('input.test').addClass('wrong');
            }
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