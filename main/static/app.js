$(function(){

    // vars

    var csrf = getCookie('csrftoken');

    var aud = $('audio')[0];

    var wordId = null;

    var log = [];

    var logPosition = 0;

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
        },
    });



    // binds

    $(window).on('keyup', function(e){
        var code = (e.charCode)? e.charCode : e.keyCode;
        if (code==13) {
            if (e.ctrlKey) {
                //skip();
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
        //console.log(code);
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

    $('button[data-action=update]').on('click', update);

    $('button[data-action=delete]').on('click', delete2);

    $(window).on('resize', resize);

    $('span.word').on('click', function(e){
        replay();
        e.stopPropagation();
    });


    $('button.next').on('click', function(e){
        next();
    });


    $('button[data-action=add-to-dict]').on('click', addToDict);

    $('button[data-action=remove-from-dict]').on('click', removeFromDict);






    // private functions



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
            logPosition--;
            setWord(ans);
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
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            log.push(ans);
            if (log.length>5) {
                log.shift();
            };
            //console.log(log);
            setWord(ans);
        }, 'json');

    }


    function setWord(ans) {

        console.log(log);
        console.log(logPosition);

        clearTimeout(tidConfirm);
        
        wordId = ans.wordId;
        progressId = ans.progessId;
        $('span.word').text(ans.word);
        setFontSize(ans.translation);
        $('.answer').text(ans.translation);
        $('input.test').focus();
        aud.src = ans.pronounce;

        var ya = 'https://translate.yandex.kz/?lang=en-ru&text=' + ans.word;
        $('a[data-action=yandex]').attr('href', ya);

        var btn1 = $('button[data-action=add-to-dict]');
        var btn2 = $('button[data-action=remove-from-dict]');
        updateButton(btn1, 'default');
        updateButton(btn2, 'default');

        if (ans.added) {
            $('.buttons').addClass('remove');
            $('.buttons').removeClass('add');
        } else {
            $('.buttons').addClass('add');
            $('.buttons').removeClass('remove');
        }

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

        var fh = $('.sticked').height();

        $('.footer-placeholder').css({
            height: fh + 'px'
        });

    }

    var tidConfirm = null;



    function addToDict() {
        addRemoveDict(true);
    }

    function removeFromDict() {
        addRemoveDict(false);
    }

    function updateButton(btn, status) {
        btn.removeClass('processing');
        btn.removeClass('default');
        btn.removeClass('done');
        btn.addClass(status);
    }



    function addRemoveDict(isAdd) {
        if (isAdd) {
            var btn = $('button[data-action=add-to-dict]');
            var url = appUrls.add;
            var newClass = 'remove';
        } else {
            var btn = $('button[data-action=remove-from-dict]');
            var url = appUrls.remove;
            var newClass = 'add';
        }        
        updateButton(btn, 'processing');
        $.post(url, {word_id: wordId}, function(ans){
            if (ans.error) {
                alert(ans.error);
                updateButton(btn, 'default');
                return false;
            }
            updateButton(btn, 'done');
            updateLog('added', isAdd);
            tidConfirm = setTimeout(function(){
                updateButton(btn, 'default');
                $('.buttons').attr('class', 'buttons ' + newClass);
            }, 2000);


        }, 'json');
    }



    function updateLog(name, value) {
        var id = log.length - logPosition - 1;
        console.log('updateLog');
        console.log(id);
        if (id < log.length && id >= 0) {
            console.log('setting to');
            console.log(log[id]);
            console.log(value);
            log[id][name] = value;
        }     
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