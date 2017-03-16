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

    var word = null;

    var log = [];

    var logPosition = 0;

    var selCollapsed = true;


    function init(){
        aud = $('audio')[0];
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

        var typeFilter = words.typeFilterValue();

        if (typeFilter=='100') {
            var data = {};
        } else {
            var data = {tf:typeFilter};
        }

        $.get(appUrls.next, data, function(ans){
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

        //console.log(log);
        //console.log(logPosition);

        clearTimeout(tidConfirm);
        
        word = ans;

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

        var newAnswer = prompt('Обновить перевод для ' + word.word  + "\n" + 'Перевод будет изменен индивидуально для Вас', word.translation);

        if (newAnswer===null) {
            return false;
        }      

        $.post(appUrls.userUpdate, {word_id: wordId, translation: newAnswer}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            $('.answer').text(newAnswer);
            word.translation = newAnswer;
        }, 'json');

    }




    function adminUpdate() {

        if (!window.isStaff) {
            return false;
        }
        
        var newAnswer = prompt('Для всех!!!' + "\n" +  'Обновить перевод для ' + word.word, word.translation);

        if (newAnswer===null) {
            return false;
        }      

        $.post(appUrls.adminUpdate, {word_id: wordId, translation: newAnswer}, function(ans){
            if (ans.error) {
                alert(ans.error);
                return false;
            }
            $('.answer').text(newAnswer);
            word.translation = newAnswer;
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



    function addToDict() {
        if (!checkAuthenticated("Добавить в словарь")) {
            return false;
        }
        addRemoveDict(true);
    }


    function removeFromDict() {
        if (!checkAuthenticated("Удалить из словаря")) {
            return false;
        }
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
            word.added = isAdd;
            //updateLog('added', isAdd);
            tidConfirm = setTimeout(function(){
                updateButton(btn, 'default');
                $('.buttons').attr('class', 'buttons ' + newClass);
            }, 2000);


        }, 'json');
    }




    /************
    *  PUBLIC
    ************/

    /*************
    *  LISTENERS
    **************/

    function listeners() {


        $(window).on('keyup', function(e){

            var code = (e.charCode)? e.charCode : e.keyCode;

            if (code==13) {
                if (e.ctrlKey) {
                    // report
                    report();
                } else {
                    console.log('next by enter');
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
                } else {
                    // remove from dict on plain delete
                    if (word.added) {
                        removeFromDict();
                    }
                }
                
            }

            // insert
            if (code==45) {
                if (e.ctrlKey) {
                    adminUpdate();
                } else {
                    userUpdate();
                }
                
            }

            // plus
            if (code==107) {
                if (!word.added) {
                    addToDict();
                }            
            }
            
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
            next();
        });


        $('button[data-action=add-to-dict]').on('click', addToDict);

        $('button[data-action=remove-from-dict]').on('click', removeFromDict);


        $('button[data-action=add-to-dict], button[data-action=remove-from-dict], button.next').on('keypress keydown keyup', function(e){
            // prevent double next action if buttons is focused
            // because pressing Enter is binded on Window
            e.stopImmediatePropagation();
            e.preventDefault();
        });


    }; // listeners


})(window.words=window.words||{});




