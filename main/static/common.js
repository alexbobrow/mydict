(function(words){


    $(function(){
        listeners();
        init();
    });

    /************
    *  PRIVATE
    ************/

    function init() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                var csrf = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            error: function(xhr, status, error){
                alert('При выполнении запроса произошла ошибка.\n'+ status + '\n' + error);
            },
        });
    }


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

    /************
    *  PUBLIC
    ************/

    words.typeFilterValue = function(){
        var value = '';
        $('button.type-filter').each(function(){
            if ($(this).hasClass('sel')) {
                value = value + '1';
            } else {
                value = value + '0';
            }
        });
        return value;
    }


    /*************
    *  LISTENERS
    **************/

    function listeners() {


        $('body').on('click', 'button.open-menu', function(){
            $('div.body').addClass('desktop-menu');
        });


        $('body').on('click', 'button[data-action=close-menu]', function(){
            $('div.body').removeClass('desktop-menu');
        });


        $('body').on('click', 'button[data-action=auth]', function(){
            $(this).parent().find('ul').slideToggle();

        });


        $('body').on('click', 'button.type-filter', function(e){
            var base = $('button.type-filter');
            if ($(this).hasClass('sel')) {

                if ($('button.type-filter.sel').length==1 && $(this).hasClass('sel')) {
                    return false;
                } else {
                    $(this).removeClass('sel');
                }
            } else {
                if (e.ctrlKey) {
                    $(this).addClass('sel');
                } else {
                    base.removeClass('sel');
                    $(this).addClass('sel');
                }
            };
        });



    }; // listeners


})(window.words=window.words||{});