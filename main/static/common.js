(function(words){

    instantInit();
    $(function(){
        listeners();
        loadedInit();
    });

    /************
    *  PRIVATE
    ************/

    function instantInit(){
        // default ajax setup
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                let csrf = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            error: function(xhr, status, error){
                alert('При выполнении запроса произошла ошибка.\n'+ status + '\n' + error);
            },
        });

        // get rid of social auth appendings
        if (window.location.href.split('#').length>1) {
            history.replaceState 
                ? history.replaceState(null, null, window.location.href.split('#')[0])
                : window.location.hash = '';
        }        
    }

    function loadedInit() {
    }

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
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
        let value = '';
        $('button.type-filter').each(function(){
            if ($(this).hasClass('sel')) {
                value = value + '1';
            } else {
                value = value + '0';
            }
        });
        return value;
    }

    words.updateUserPrefs = function(name, value) {
        if (window.isAuthenticated) {
            let data = {};
            data[name] = value;
            $.ajax({
               type: 'PATCH',
               url: appUrls.userPrefs,
               data: JSON.stringify(data),
               processData: false,
               contentType: 'application/json',
            });
        }
    }

    /*************
    *  LISTENERS
    **************/

    function listeners() {

        let body = $('body');

        body.on('click', 'button.toggle-menu', function(){
            $('div.body').toggleClass('menu-opened');
            let new_value = $('div.body').hasClass('menu-opened');
            words.updateUserPrefs('show_sidebar', new_value);
        });

        body.on('click', 'button[data-action=auth], button[data-action=user]', function(){
            $(this).parent().find('ul').slideToggle();

        });

        body.on('click', 'button.type-filter', function(e){
            let menu = $(this).closest('.menu');
            if (menu.hasClass('disabled')) {
                return false;
            }
            let base = $('button.type-filter');
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
            }

            // callbacks
            if (words.typeFilterList) {
                words.typeFilterList(e);
            }
            if (words.typeFilterCards) {
                words.typeFilterCards(e);
            }
            
        });

        body.on('click', 'a.login-required', function(e){
            if (!isAuthenticated) {
                alert('Для этой страницы необходимо авторизоваться.');
                e.preventDefault();
            }
        });
    } // listeners

})(window.words=window.words||{});
