(function(words){


    $(function(){
        listeners();
        init();
    });

    /************
    *  PRIVATE
    ************/

    var aud;

    var wordId = null;

    var currentData = null;

    var log = [];

    var logPosition = 0;

    var selCollapsed = true;

    var debug = (window.localStorage.getItem('debug')==='true');

    var answerDelay = (window.localStorage.getItem('answerDelay')==='true');

    var filters = '';


    var numRules = [
        ['1', [97, 49]],
        ['2', [98, 50]],
        ['3', [99, 51]],
        ['4', [100, 52]],
        ['5', [101, 53]],
    ];



    function init(){
        aud = $('audio')[0];

        // show debug if needed
        if (debug) {
            $('table.debug').show();
        }

        if (answerDelay) {
            $('button[data-action=answer-delay]').addClass('checked');
        }

        
        console.log('next initial');
        next();
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
            logPosition--;
            setWord(ans);
        }     
    }



    function next(data) {



        if ($('body').hasClass('next-processing')) {
            return false;
        }

        $('body').addClass('next-processing');

        if (logPosition<0) {
            //console.log('log pos < 0');
            var id = log.length + logPosition;
            //console.log('id', id);
            var ans = log[id];
            setWord(ans);
            logPosition++;
            return
        }

        if (typeof(data)=='undefined') {
            data = {};
        }
        
        if (filters!='') {
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
            };
            //console.log(log);
            setWord(ans);
        }, 'json').always(function(){
            $('body').removeClass('next-processing');
            console.log('next request finished');
        });

    }


    function setWord(ans) {

        var btn = $('button.next');

        clearTimeout(tidConfirm);
        
        currentData = ans;

        wordId = ans.wordId;
        progressId = ans.progessId;
        $('span.word').text(ans.en);
        setFontSize(ans.ru);
        $('.answer').text(ans.ru);
        $('input.test').focus();
        aud.src = ans.pronounce;

        var lg = 'http://www.lingvo.ua/ru/Translate/en-ru/' + ans.en;
        $('a[data-action=lingvo]').attr('href', lg);

        var rv = 'http://context.reverso.net/перевод/английский-русский/' + ans.en;
        $('a[data-action=reverso]').attr('href', rv);

        // stata
        $('span.stata-new').text(ans.newTotal);
        $('span.stata-all').text(ans.total);
        $('span.stata-5').text(ans.progress5);
        $('span.stata-4').text(ans.progress4);
        $('span.stata-3').text(ans.progress3);
        $('span.stata-2').text(ans.progress2);
        $('span.stata-1').text(ans.progress1);
        

        if (answerDelay) {
            $('body').addClass('answer-delay');
        }

        if (ans.knowLast && ans.knowLast>0) {
            console.log('setting to ' + ans.knowLast);
            $('button[data-know='+ans.knowLast+']').focus();
        }

        // debug
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




    function userUpdate() {

        if (!checkAuthenticated('Изменить перевод')) {
            return false;
        }

        var newAnswer = prompt('Обновить перевод для ' + currentData.en  + "\n" + 'Перевод будет изменен индивидуально для Вас', currentData.ru);

        if (newAnswer===null) {
            return false;
        }      

        $.post(appUrls.userUpdate, {word_id: wordId, translation: newAnswer}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            $('.answer').text(newAnswer);
            currentData.ru = newAnswer;
        }, 'json');

    }




    function adminUpdate() {

        if (!window.isStaff) {
            return false;
        }
        
        var newAnswer = prompt('Для всех!!!' + "\n" +  'Обновить перевод для ' + currentData.en, currentData.ru);

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
        $.post(url, {word_id: wordId}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            word.added = isAdd;
            next();

        }, 'json');
    }



    function answer(value){

        var data = {
            answer_value: value,
            progress_id: currentData.progressId
        }

        next(data);

    }

    function setActive(value) {
        $('button[data-know]').removeClass('active');
        $('button[data-know='+value+']').addClass('active');
        $('button[data-know='+value+']').focus();
    }


    function saveFilters() {

        filters = '';
        var all = '';

        $('button[data-filter]').each(function(){
            if ($(this).hasClass('checked')) {
                filters += $(this).attr('data-filter');
            }
            all += $(this).attr('data-filter');
        });

        if (all==filters) {
            filters = '';
        }

        console.log(filters);

    }




    /************
    *  PUBLIC
    ************/



    /*************
    *  LISTENERS
    **************/

    function listeners() {


        $(window).on('keyup', function(e){

            /*

            if (code==13) {
                if (e.ctrlKey) {
                    // report
                    report();
                } else {
                    console.log('next by enter');
                    var btn = $('button.next');
                    next();
                }
            }

            // backspace
            if (code==8) {
                prev();
            }

            // space
            if (code==32) {
                replay();
            }

            // delete
            if (code==46) {
                if (e.ctrlKey) {
                    // admin disable word if ctrl
                    disable();
                }                
            }

            */
            
            var code = (e.charCode)? e.charCode : e.keyCode;
            
            if (code==38) {
                replay();
            }

            // insert
            if (code==45) {
                if (e.ctrlKey) {
                    adminUpdate();
                } else {
                    userUpdate();
                }
            }


            // r - reverso
            if (code==82) {
                var w = window.open($('a[data-action=reverso]').attr('href'));
            }

            // l - lingvo
            if (code==76) {
                var w = window.open($('a[data-action=lingvo]').attr('href'));
            }



            $('.buttons button').removeClass('active');
            console.log(code);
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


        $('button[data-action=update]').on('click', function(e){
            if (e.ctrlKey) {
                adminUpdate();
            } else {
                userUpdate();
            }

        });

        $('button[data-action=delete]').on('click', disable);

        $(window).on('resize', resize);

        $('span.word').on('click', function(e){
            replay();
            e.stopPropagation();
        });


        $('button.next').on('click', function(e){
            var btn = $('button.next');
            next();
        });



        $('button[data-action=add-to-dict], button[data-action=remove-from-dict], button.next').on('keypress keydown keyup', function(e){
            // prevent double next action if buttons is focused
            // because pressing Enter is binded on Window
            // e.stopImmediatePropagation();
            e.preventDefault();
        });


        $('button[data-know]').on('click', function(e){
            var value = $(this).attr('data-know');
            answer(value);
        });


        $(window).on('keydown', function(e){
            var code = e.keyCode;         
            $.each(numRules, function(k,v){
                if (v[1].indexOf(code)>=0) {
                    setActive(v[0]);
                }
            });
        });


        $('button[data-know]').on('keydown', function(e){
            var code = e.keyCode;
            if (code==13) {
                var value = $(this).attr('data-know');
                setActive(value);
                e.preventDefault();
            }
        });


        $('button[data-know]').on('keyup', function(e){
            var code = e.keyCode;
            var value = parseInt($(this).attr('data-know'),10);
            
            if (code==39) {
                // right
                value++;
                if (value==6) {
                    value=1;
                }
                $('button[data-know='+value+']').focus();
            }

            if (code==37) {
                // left
                value--;
                if (value==0) {
                    value=5;
                }
                $('button[data-know='+value+']').focus();
            }


            if (code==13) {
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
            var code = e.keyCode;
            if (code==13) {
                e.preventDefault();
            }
            $(this).addClass('active');
        });


        $('.buttons button[data-action]').on('keyup', function(e){
            var code = e.keyCode;
            if (code==13) {
                next();
                e.preventDefault();
            }
        });



        $('button[data-action=debug]').on('click', function(e){
            e.preventDefault();
            if ($('table.debug').is(':visible')) {
                $('table.debug').hide();
                window.localStorage.setItem('debug', 'false');
            } else {
                $('table.debug').show();
                window.localStorage.setItem('debug', 'true');
            }
        });



        $('button.checkbox').on('click', function(e){
            $(this).toggleClass('checked');
        });



        $('button[data-action=answer-delay]').on('click', function(e){
            if ($(this).hasClass('checked')) {
                answerDelay = true;
                localStorage.setItem('answerDelay', 'true');
            } else {
                answerDelay = false;
                localStorage.setItem('answerDelay', 'false');
            }
        });


        $('button[data-filter]').on('click', function(e){
            saveFilters();
        });




        $('html').on('click', function(e){
            if (answerDelay) {
                $('body').removeClass('answer-delay');
            }
        });





    }; // listeners


})(window.words=window.words||{});




