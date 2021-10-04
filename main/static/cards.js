(function(words){

    let body;

    $(function(){
        body = $('body');
        listeners();
        init();
    });

    /************
    *  PRIVATE
    ************/

    let aud;

    let wordId = null;

    let currentData = null;

    let log = [];

    let logPosition = 0;

    let numRules = [
        ['1', [97, 49]],
        ['2', [98, 50]],
        ['3', [99, 51]],
        ['4', [100, 52]],
        ['5', [101, 53]],
    ];

    function init(){
        aud = $('audio')[0];
        next();
    }

    function replay() {
        if (aud.src !== '') {
            aud.play();
        }
    }

    function prev() {
        let newPos = logPosition-1;
        let id = log.length + newPos-1;
        if (id < log.length && id >= 0) {
            let ans = log[id];
            logPosition--;
            setWord(ans);
        }     
    }

    function next(data) {

        if (body.hasClass('next-processing')) {
            return false;
        }

        body.addClass('next-processing');

        if (logPosition < 0) {
            let id = log.length + logPosition;
            let ans = log[id];
            setWord(ans);
            logPosition++;
            return
        }

        if (typeof(data)=='undefined') {
            data = {};
        }

        let filters = getFilters();
        if (filters !== '') {
            data['filters'] = filters;
        }

        $.post(appUrls.next, data, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            log.push(ans);
            if (log.length>5) {
                log.shift();
            }
            setWord(ans);
        }, 'json').always(function(){
        });

    }

    function setWord(ans) {

        clearTimeout(tidConfirm);
        
        currentData = ans;

        wordId = ans.word.id;
        $('span.word').text(ans.word.en);
        setFontSize(ans.word.ru);
        $('.answer').text(ans.word.ru);
        $('input.test').focus();
        aud.src = ans.word.pronounce;

        body.removeClass('next-processing');

        $('a[data-action=auto-link]').each(function(){
            let tpl = $(this).attr('data-template');
            let re = /{word}/;
            let newHref = tpl.replace(re, ans.word.en);
            $(this).attr('href', newHref)
        })

        // stata
        if (ans.stats) {
            $('span.stata-new').text(ans.stats.newTotal);
            $('span.stata-all').text(ans.stats.total);
            $('span.stata-5').text(ans.stats.progress5);
            $('span.stata-4').text(ans.stats.progress4);
            $('span.stata-3').text(ans.stats.progress3);
            $('span.stata-2').text(ans.stats.progress2);
            $('span.stata-1').text(ans.stats.progress1);
        }

        if (checked('answer-delay')) {
            body.addClass('answer-delay');
        }

        if (ans.progress && ans.progress.knowLast > 0) {
            $('button[data-know='+ans.progress.knowLast+']').focus();
        }

        resize();
    }

    function setFontSize(str) {
        let len = str.length;
        let sizeClass = 's1';
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

    function checkAuthenticated(name) {
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

        if (!checkAuthenticated('Сообщить об ошибке')) {
            return false;
        }

        let word = $('span.word').text();
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

    function adminUpdate() {

        if (!window.isStaff) {
            return false;
        }
        
        let newAnswer = prompt('Для всех!!!' + "\n" +  'Обновить перевод для ' + currentData.en, currentData.ru);

        if (newAnswer===null) {
            return false;
        }      

        $.post(appUrls.adminUpdate, {word_id: wordId, translation: newAnswer}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            $('.answer').text(newAnswer);
            currentData.ru = newAnswer;
        }, 'json');
    }

    function disable(e) {

        if (typeof(e)!=='undefined') {
            e.stopPropagation();
        }      

        if (!window.isStaff) {
            return false;
        }

        let word = $('span.word').text();
        if (!confirm('УДАЛИТЬ слово "'+word+'"?')) {
            return false;
        }
        $.post(appUrls.delete, {word_id: wordId}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            next();
        }, 'json');
    }

    function resize() {

        let fh = $('.sticked').height();

        $('.footer-placeholder').css({
            height: fh + 'px'
        });

    }

    let tidConfirm = null;

    function answer(value){
        let data = {
            answer_value: value,
            progress_id: currentData.progressId
        }
        next(data);
    }

    function setActive(value) {
        $('button[data-know]').removeClass('active');
        $('button[data-know='+value+']').addClass('active').focus();
    }

    function getFilters() {

        let filters = '';
        let all = '';

        $('button[data-filter]').each(function(){
            if ($(this).hasClass('checked')) {
                filters += $(this).attr('data-filter');
            }
            all += $(this).attr('data-filter');
        });

        if (all === filters) {
            filters = '';
        }
        return filters;
    }

    function saveFilters() {
        let filters = getFilters();
        words.updateUserPrefs('filters', filters);
    }

    function checked(action) {
        return $('button.checkbox[data-action='+action+']').hasClass('checked');
    }

    /************
    *  PUBLIC
    ************/

    /*************
    *  LISTENERS
    **************/

    function listeners() {

        $(window).on('keyup', function(e){

            let code = (e.charCode)? e.charCode : e.keyCode;

            /*

            if (code==13) {
                if (e.ctrlKey) {
                    // report
                    report();
                } else {
                    let btn = $('button.next');
                    next();
                }
            }

            // space
            if (code==32) {
                replay();
            }

            */

            // backspace
            if (code === 8) {
                prev();
            }

            // up
            if (code === 38) {
                replay();
            }

            // insert
            if (code === 45) {
                adminUpdate();
            }

            // delete
            if (code === 46) {
                disable();
            }

            if (code === 39) {
                // right
                let dataKnow = $(document.activeElement).attr('data-know');
                if (typeof(dataKnow)=='undefined') {
                    $('button[data-know=1]').focus();
                }
            }

            if (code === 37) {
                // left
                let dataKnow = $(document.activeElement).attr('data-know');
                if (typeof(dataKnow)=='undefined') {
                    $('button[data-know=5]').focus();
                }
            }

            $('.buttons button').removeClass('active');
        });

        $('button[data-action=disable]').on('click', function(e){
            if (!confirm('Отключить это слово?')) {
                return false;
            }
            let data = {
                progress_id: currentProgressId,
                csrfmiddlewaretoken: csrf,
            }
            $.post(appUrls.disable, data, function(ans){
                next();
            }, 'json');            
        });

        $('button[data-action=report]').on('click', report);

        $('button[data-action=update]').on('click', function(e){
            adminUpdate();
        });

        $('button[data-action=delete]').on('click', disable);

        $(window).on('resize', resize);

        $('span.word').on('click', function(e){
            replay();
            e.stopPropagation();
        });

        $('button.next').on('click', function(e){
            let btn = $('button.next');
            next();
        });

        $('button[data-action=add-to-dict], button[data-action=remove-from-dict], button.next').on('keypress keydown keyup', function(e){
            // prevent double next action if buttons is focused
            // because pressing Enter is binded on Window
            // e.stopImmediatePropagation();
            e.preventDefault();
        });

        $('button[data-know]').on('click', function(e){
            if (!checkAuthenticated('Указать уровень знания по шкале 1-5')) {
                return false;
            }
            let value = $(this).attr('data-know');
            answer(value);
        });

        $(window).on('keydown', function(e){
            let code = e.keyCode;
            $.each(numRules, function(k,v){
                if (v[1].indexOf(code)>=0) {
                    setActive(v[0]);
                }
            });
        });

        $('button[data-know]').on('keydown', function(e){
            let code = e.keyCode;
            if (code === 13) {
                let value = $(this).attr('data-know');
                setActive(value);
                e.preventDefault();
            }
        });

        $('button[data-know]').on('keyup', function(e){
            let code = e.keyCode;
            let value = parseInt($(this).attr('data-know'),10);
            
            if (code === 39) {
                // right
                value++;
                if (value === 6) {
                    value=1;
                }
                $('button[data-know='+value+']').focus();
            }

            if (code === 37) {
                // left
                value--;
                if (value === 0) {
                    value=5;
                }
                $('button[data-know='+value+']').focus();
            }

            if (code === 13) {
                answer(value);
            }

            $.each(numRules, function(k,v){
                if (v[1].indexOf(code)>=0) {
                    answer(value);
                }
            });

        });

        $('.buttons button[data-action]').on('click', function(e){
            next();
        });

        $('.buttons button[data-action]').on('keydown', function(e){
            let code = e.keyCode;
            if (code === 13) {
                e.preventDefault();
            }
            $(this).addClass('active');
        });

        $('.buttons button[data-action]').on('keyup', function(e){
            let code = e.keyCode;
            if (code === 13) {
                next();
                e.preventDefault();
            }
        });

        $('button.checkbox').on('click', function(e){
            $(this).toggleClass('checked');
        });

        $('button[data-action=answer-delay]').on('click', function(e){
            let new_value = $(this).hasClass('checked');
            words.updateUserPrefs('answer_delay', new_value);
        });

        $('button[data-filter]').on('click', function(e){
            if (!checkAuthenticated('Фильтр слов по уровню знания')) {
                return false;
            }
            saveFilters();
        });

        $('html').on('click', function(e){
            if (checked('answer-delay')) {
                body.removeClass('answer-delay');
            }
        });

    } // listeners

})(window.words=window.words||{});
