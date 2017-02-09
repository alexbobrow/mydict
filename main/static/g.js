(function(alex){

    /*
    DEBUGGING jQuery addition

    var elem = document.createElement('script');
    elem.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.2.3/jquery.min.js";
    document.body.appendChild(elem);

    */


    // init jQuery
    // $ visible only in the local scope
    var oldDollar = window['$'];
    var $ = null;
    var elem = document.createElement('script');
    elem.onload = function(){
        jQuery.noConflict();
        $ = jQuery;
        window['$'] = oldDollar;
        alex.init();
    }
    elem.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.2.3/jquery.min.js";
    document.body.appendChild(elem);



    // adding buttons
    alex.init = function(){
        $('#gt-appname').after("<button data-action='start'>start</button><button data-action='stop'>stop</button><button data-action='one'>one</button>");

        buttonsState();

        $('body').on('click', 'button[data-action=start]', function(e){
            e.stopPropagation();
            e.preventDefault();
            alex.start();
        });

        $('body').on('click', 'button[data-action=stop]', function(e){
            e.stopPropagation();
            e.preventDefault();
            alex.stop();
        });


        $('body').on('click', 'button[data-action=one]', function(e){
            e.stopPropagation();
            e.preventDefault();
            alex.one();
        });
    };
    


    function buttonsState() {
        if (on) {
            $('button[data-action=start]').hide();
            $('button[data-action=one]').hide();
            $('button[data-action=stop]').show();
        } else {
            $('button[data-action=start]').show();
            $('button[data-action=one]').show();
            $('button[data-action=stop]').hide();
        }
    }




    var pauseTid = 0;
    var listenTid = 0;
    var on = false;
    var previousTranslation = null;
    var wordId = null;


    alex.start = function(){
        on = true;
        buttonsState();
        alex.next();
        return 'started';
    };


    alex.stop = function(){
        clearTimeout(pauseTid);
        on = false;
        buttonsState();
        return 'stopped';
    };


    alex.one = function(){
        on = true;
        buttonsState();
        alex.next();
        on = false;
        buttonsState();
    }


    alex.next = function(){

        if (!on) {
            return false;
        }

        
        $.get('https://mydict.loc:8050/api/tmp/next', {}, function(ans){

            if (!ans.ok) {
                console.log(ans.error);
                alex.stop();
            }

            document.location.href = '/#en/ru/' + ans.word;
            wordId = ans.id;

            listenTid = setInterval(listenTranslation, 300);
            
        }, 'json');

    }




    function listenTranslation(){
        var currentTranslation = $('.gt-cc-l')[0].innerHTML;
        if (previousTranslation!=currentTranslation) {
            clearInterval(listenTid);
            saveTranslation();
        }
    }





    function saveTranslation() {
        
        var data = parseTranslation();

        if (typeof(data)=='boolean') {
            alex.stop();
            return false;
        }

        data.push({
            name: 'word_id',
            value: wordId
        });

        $.post('https://mydict.loc:8050/api/tmp/trs', data, function(ans){

            if (!ans.ok) {
                console.log(ans.error);
                previousTranslation = null;
                alex.stop();
            }

            previousTranslation = $('.gt-cc-l')[0].innerHTML;

            planNext();
            
        }, 'json');


    }




    function planNext() {
        pauseTid = setTimeout(alex.next, 3000);
    }




    function parseTranslation() {

        if (!$("#result_box").length) {
            console.log('Error! No result box');
            return false;
        }

        var main = $('#result_box').text().toLowerCase();
        var words = [];

        /*data.push({
            name: 'word',
            value: main
        });*/

        if ($.trim(main)!='') {
            words.push(main);
        }

        // base or not
        if (!$("#source").length) {
            console.log('Error! No texratea');
            return false;
        }

        if (
            $("#source").length &&
            $(".gt-cc-r .gt-card-ttl-txt").length &&
            $("#source").val() == $(".gt-cc-r .gt-card-ttl-txt").text()
        ) {
            var base = true;
        } else {
            base = false;
        }


        var data = [{
            name: 'base',
            value: base
        }];
        



        // other translation suggestions
        $('.gt-baf-table:visible tr').each(function(){
            if ($(this).find('td').length!=3) {
                return true;
            }

            var bar = $(this).find('.gt-baf-cts');
            if (bar.length<1) {
                return true;
            }

            var width = bar.width();
            var word = $(this).find('.gt-baf-word-clickable').text();

            if ((width==24 || width==16) && $.inArray(word, words)<0) {
                words.push(word);
            }
        });


        // flat array to POST object
        $.each(words, function(k, v){
            data.push({
                name: 'word',
                value: v
            });

        });



        return data;

    }


})(window.alex = window.alex || {});

