(function(words){

    $(function(){
        listeners();
        init();
    });

    /************
    *  PRIVATE
    ************/

    let aud;

    function init() {
        aud = $('audio')[0];
    }

    /************
    *  PUBLIC
    ************/

    /*************
    *  LISTENERS
    **************/

    function listeners() {

        $('body').on('click', 'button[data-action=pronounce]', function(e){
            aud.src = $(this).attr('data-url');
        });

        $('body').on('click', '.words-row span.hover', function(e){
            let col = $(this).closest('.translation');
            col.removeClass('idle');
            col.addClass('edit');
            let i = col.find('input[type=text]');
            i[0].selectionStart = i[0].selectionStart = i.val().length;
            i.focus();
        });

        $('body').on('submit', '.edit-translation form', function(e){
            e.preventDefault();
            let col = $(this).closest('.translation');
            let input = col.find('input[name=translation]');
            let data = $(this).serializeArray();
            $.post(appUrls.update, data, function(ans){
                col.find('span.hover').text(input.val());
                col.addClass('custom');
                col.addClass('idle');
                col.removeClass('edit');
            }, 'json');

        });

        $('body').on('click', 'button[data-action=translation-cancel]', function(e){
            e.preventDefault();
            let col = $(this).closest('.translation');
            col.removeClass('edit');
            col.addClass('idle');            
        });

    } // listeners

})(window.words=window.words||{});
