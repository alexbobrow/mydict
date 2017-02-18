$(function(){

    // vars

    var csrf = getCookie('csrftoken');

    var aud = $('audio')[0];

    var wordId = null;

    var log = [];

    var logPosition = 0;

    var clickBlockTid = null;

    var clickBlock = false;

    var selCollapsed = true;

    // initialization

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        },
        error: function(xhr, status, error){
            alert('При выполнении запроса произошла ошибка.\n'+ status + '\n' + error);
        }
    });



    // binds

    $(window).on('keyup', function(e){
        var code = (e.charCode)? e.charCode : e.keyCode;
        if (code==13) {
            if (e.ctrlKey) {
                skip();
            } else if (e.shiftKey) {
                report();
            } else {
                console.log('next by enter');
                next();
            }
        }
        if (code==8) {
            prev();
        }
        if (code==32) {
            replay();
        }
        if (code==46) {
            delete2();
        }
        if (code==45) {
            update();
        }
        console.log(code);
    });


    
    $(window).on('blur', function(e){
        clearTimeout(clickBlockTid);
        clickBlock = true;
        console.log('block on blur');
    });


    $(window).on('focus', function(e){
        clickBlockTid = setTimeout(function(){
            clickBlock = false;
            console.log('release on focus');
        }, 300);
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
            console.log('next by disabled cb');
            next();
        }, 'json');            
    });

   
    $('button[data-action=report]').on('click', report);

    $('button[data-action=skip]').on('click', skip);

    $('button[data-action=update]').on('click', update);

    $('button[data-action=delete]').on('click', delete2);

    $(window).on('resize', resize);

    $('span.word').on('click', function(e){
        replay();
        e.stopPropagation();
    });

    

    
    $(document).on('selectionchange', function(e){
        // block click if user selecting text
        var s = window.getSelection();
        if (!s.isCollapsed) {
            clickBlock = true;
            selCollapsed = false;
            console.log('block on select');
        } else {
            if (!selCollapsed) {
                console.log('block on just collapsed');
                selCollapsed = true;
                clickBlock = true;
            }
        }
    });



    $('body').on('click', function(e){
        click();
    });

    
    $('.next-click-area').on('click touchend', function(e){
        click();
    });



    $('.footer a').on('click', function(e){
        e.stopPropagation();
    });



    // private functions

    function click() {
        if (!clickBlock) {
            console.log('next by click on body');
            next();
        } else {
            if (!selCollapsed) {
                return false;
            }
            // release if blocked by selection
            console.log('relese after click when blocked');
            clickBlock = false;
        }
    }


    function replay() {
        if (aud.src!='') {
            aud.play();
        }
    }


    function prev() {
        //console.log('prev');
        var newPos = logPosition-1;
        //console.log('newPos', newPos);
        var id = log.length + newPos-1;
        //console.log('id', id);
        if (id < log.length && id >= 0) {
            var ans = log[id];
            setWord(ans);
            logPosition--;
        }     
        
    }


    function next() {


        if (logPosition<0) {
            //console.log('log pos < 0');
            var id = log.length + logPosition;
            //console.log('id', id);
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
            //console.log(log);
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

        var ya = 'https://translate.yandex.kz/?lang=en-ru&text=' + ans.word;
        $('a[data-action=yandex]').attr('href', ya);

        resize();

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



    function check_authenticated(name) {
        if (!window.isAuthenticated) {
            alert('Для работы функции "'+name+'" необходимо авторизоваться.');
            return false;
        } else {
            return true;
        }
    }


    function report(e) {

        if (typeof(e)!=='undefined') {
            e.stopPropagation();
        }

        if (!check_authenticated('Сообщить об ошибке')) {
            return false;
        }

        var word = $('span.word').text();
        if (!confirm('Сообщить об ошибке/неточности в слове "'+word+'"?')) {
            return false;
        }
        $.post(appUrls.report, {word_id: wordId}, function(ans, x){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            next();
        }, 'json');
    }



    function skip(e) {

        if (typeof(e)!=='undefined') {
            e.stopPropagation();
        }      
        
        if (!check_authenticated('Исключить/Не показывать')) {
            return false;
        }

        var word = $('span.word').text();
        if (!confirm('Исключить слово "'+word+'"?\nДанное слово больше не будет вам показываться.')) {
            return false;
        }
        $.post(appUrls.skip, {word_id: wordId}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            console.log('next by skip cb');
            next();
        }, 'json');
    }




    function update(e) {

        if (typeof(e)!=='undefined') {
            e.stopPropagation();
        }      

        if (!window.isStaff) {
            return false;
        }
        
        var word = $('span.word').text();
        var answer = $('.answer').text();
        var newAnswer = prompt('Обновить перевод для ' + word, answer);

        if (newAnswer===null) {
            return false;
        }      

        $.post(appUrls.update, {word_id: wordId, translation: newAnswer}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            $('.answer').text(newAnswer);
        }, 'json');
    }




    function delete2(e) {

        if (typeof(e)!=='undefined') {
            e.stopPropagation();
        }      

        if (!window.isStaff) {
            return false;
        }

        var word = $('span.word').text();
        if (!confirm('УДАЛИТЬ слово "'+word+'"?')) {
            return false;
        }
        $.post(appUrls.delete, {word_id: wordId}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            console.log('next by delete cb');
            next();
        }, 'json');
    }


    function resize() {

        var marker = $('.pos-marker').position();

        var top = marker.top;
        var fh = $('.footer').height();
        var bh = $(window).height();

        var ch = bh - fh - top;
        $('.next-click-area').css({
            top: top + 'px',
            height: ch + 'px'
        });

        $('.footer-placeholder').css({
            height: fh + 'px'
        });

    }




    console.log('next initial');

    next();


}); // dom ready



function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


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