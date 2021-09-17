(function(){

    /*
    alexSuggest v4.1
    fork for mydict
    */

    /* global */

    let popupId = 'alsuli'
    let selectorPopup = '#' + popupId;
    let selectorLi = selectorPopup + " li";

    let queryTid = 0;
    let blurTid = 0;
    let xhr = null;

    window.alexSuggest = function(selector, params){

        let body = $('body');

        createContainer(body);

        let defaultParams = {
            // класс который проставляется активной ссылке в popup
            hoverClass: 'alsuli-cur', 
            // путь для запроса
            url: "/", 
            // bool, если true по интеру текст активного пункта проставляется в поле
            autoValueText: false, 

            // массив 1) jQuery(<input>) инпут в который автоматически проставится 2) str:атрибут
            autoValueAttr: null, 
            /* указывает как определять уникальность элементов например 'data-id' или 'text()'
            если указать будет отмечать выбраннный ранее пункт при повторном раскрытии списка */     
            uniquePart: null,  
            /* не запускает onSelect при повторном нажатии работает только если указать
            uniquePart */
            ignoreRepeat: false, 
            postParams: {},
            inputOffsetTop: 0,
            inputOffsetLeft: 0,
            inputOffsetWidth: 0,
            minWordCount: 0,
            /* класс который дополнительно проставляется основному контейнеру */
            setClass: "", 
            /* перед запросом, без параметров */
            onQueryBefore: function(){},
            /* после запросом, без параметров */ 
            onQueryAfter: function(){}, 
            /* калбак выбора, один параметр - сырой выбранный элемент */
            onSelect: function(){}, 
            /* калбак отмена (потеря фокуса, клик по боди) */
            onCancel: function(){}, 
            /* калбак интера без выбора, без параметров */
            onPlainEnter: function(){}, 
            /* выхывается при смене подсвечивающегося пункта, по стрелкам или при наведении
            один параметр - сырой подсвеченый элемент */
            onSelectionChange: function(){}  
        };

        body.on('click', selector, function(e){
            $(this).keyup();
            e.stopPropagation();
        });

        body.on('blur', selector, function(e){
            let i = $(this);
            // при клике на попап без блюра все портится
            blurTid = setTimeout(function(){
                cancel(i);
            }, 200);          
        });

        // блокировка отрпавки формы
        body.on('keypress', selector, function(e){
            let code = (e.charCode)? e.charCode : e.keyCode;
            if (code === 13) {
                e.preventDefault();
                e.stopPropagation();
            }

        });

        body.on('keyup', selector, function(e){

            let o = getObject(params, defaultParams, this);
            let i = $(this);
            
            console.log('clear timeout');
            clearTimeout(queryTid);
            if (xhr) {
                xhr.abort();
            }
            
            let code = (e.charCode)? e.charCode : e.keyCode;

            
            if (code === 38) {
                up(i);
                return true;
            }       
            
            if (code === 40) {
                down(i);
                return true;
            }
            
            if (code === 13) {
                console.log('enter');
                enter(i);
                e.preventDefault();
                e.stopPropagation();
                return false;
            }       
            

            let wordsCount = i.val().length;
            if (wordsCount === 0) {
                cancel(i);
                return false;
            }

            if (wordsCount<o.minWordCount) {
                return false;
            }

            // далее обработка нажатия любой другой клавиши, предлположительно новая буква
            console.log('set timeout');
            queryTid = setTimeout(function(){
                console.log('timeout callback');
                o.onQueryBefore(i);
                o.postParams.value = i.val();
                xhr = $.get(o.url, o.postParams, function(data){
                    o.onQueryAfter(i);
                    showPopup(i, data);
                }, 'html');
            },300);
        
        });

        $(selector).each(function(e){
            getObject(params, defaultParams, this);
        });

    } // w.as

    function getObject(defaultParams, params, input) {
        let i = $(input);

        if (typeof(i.data('alexSuggest'))=='undefined') {

            let o = $.extend({}, params, defaultParams);
            i.data('alexSuggest', o);
            o.initialValue = i.val();
            return o;

        } else {
            return i.data('alexSuggest');
        }

    }

    function up(i){

        if (!$(selectorPopup).length) return;

        let length = $(selectorLi).length;
        if (length<1) return;

        let o = i.data('alexSuggest');
        let selectorHover = selectorLi + '.' + o.hoverClass

        let index = $(selectorLi).index($(selectorHover));
        let new_index = (index-1) ;

        if (new_index<0) { new_index = (length-1); }

        $(selectorHover).removeClass(o.hoverClass);
        
        let newSelected = $(selectorLi + ":eq("+new_index+")");
        newSelected.addClass(o.hoverClass);
        
        o.onSelectionChange(i, newSelected);
        
    }

    function down(i) {

        if (!$(selectorPopup).length) return;

        let length = $(selectorLi).length;
        if (length<1) return;

        let o = i.data('alexSuggest');
        let selectorHover = selectorLi + '.' + o.hoverClass

        let index = $(selectorLi).index($(selectorHover));

        if (index < 0) {
            index = 0;
        } else {
            index++;
            if (index === length) {
                index = 0;
            }
        }

        $(selectorHover).removeClass(o.hoverClass);
        
        let newSelected = $(selectorLi + ":eq("+index+")");
        newSelected.addClass(o.hoverClass);
        
        o.onSelectionChange(i, newSelected);

    }

    /**
     * при нажатии на интер по полю
     */
    function enter(i) {
        
        let o = i.data('alexSuggest');
        
        let jElem = $(selectorPopup + " ." + o.hoverClass);
        
        if (jElem.length) { // выбран выриант
           
           select(i, jElem);

           // прячется в select'e         
        } else { // просто итнер

            // сбрасываем автопроставляемое поле
            if (o.autoValueAttr!==null) {
                o.autoValueAttr[0].val('');
            }

            // калбак
            o.onPlainEnter(i);

            $(selectorPopup).empty().hide();
            o.processedUnique = null;
            
        }

    }

    /**
     * принажатии на интер по полю если есть выделенный элемент
     * или клик по элементы мышкой
     * input - текущее поле, jQuery
     * element - выбранный пункт, jQuery
     * 
     */
    function select(i, li){

        let o = i.data('alexSuggest');

        let unique = getUniqueValue(i, li);
        if (unique &&  o.ignoreRepeat && o.processedUnique && o.processedUnique === unique) {
            $(selectorPopup).empty().hide();
            return false;
        }

        if (o.autoValueText) {
            i.val(li.text());
        }
        
        if (o.autoValueAttr!==null) {
            let autoInput = o.autoValueAttr[0];
            let attrName = o.autoValueAttr[1];
            if (typeof(li.attr(attrName))!='undefined') {
                autoInput.val(li.attr(attrName));
            }
        }

        if (unique) {
            o.processedUnique = unique;
        }

        o.onSelect(i, li);
        
        $(selectorPopup).empty().hide();
    }

    function cancel(i) {
        // калбак
        let o = i.data('alexSuggest');
        o.onCancel(i);
        $(selectorPopup).empty().hide();
    }

    function getUniqueValue(i, li) {
        let o = i.data('alexSuggest');
        if (o.uniquePart) {
            if (o.uniquePart === 'text()') {
                return li.text();
            } else {
                if (typeof(li.attr(o.uniquePart))!='undefined') {
                    return li.attr(o.uniquePart);
                } else {
                    return null;
                }
            }
        } else {
            return null;
        }

    }

    /**
     * data - ответ XML запроса
     * input - сырой элемент поля
     */
    function showPopup(i, data) {

        let o = i.data('alexSuggest');

        let popupOffset = i.offset();
        
        $(selectorPopup).css({
            top: (popupOffset.top + i.height() + o.inputOffsetTop) + "px",
            left: (popupOffset.left + o.inputOffsetLeft) + "px",
            width: (i.width() + o.inputOffsetWidth) + "px"
        });

        $(selectorPopup).html(data);

        if (o.setClass !== '') {
            $(selectorPopup).attr('class', o.setClass);
        } else {
            $(selectorPopup).attr('class', '');
        }
        
        if ($(selectorLi).length) {
            $(selectorPopup).show();
        } else {
            $(selectorPopup).hide();
        }
        
        $(selectorPopup).data('input', i);
        
        // отметим ранее выбранный, если актуально
        $(selectorLi).each(function(){           
            let unique = getUniqueValue(i, $(this));
            if (unique === o.processedUnique) {
                $(this).addClass(o.hoverClass);
            }
        });
        
    }

    function createContainer(body) {

        if ($(selectorPopup).length) {
            $(selectorPopup).empty();
            return;
        }

        body.append($("<div id='"+popupId+"' style='display:none'></div>").hover(function(){ $(this).addClass("hover"); },function(){ $(this).removeClass("hover"); }));

        body.on('click', selectorLi, function(e){
            let i = $(selectorPopup).data('input');
            clearTimeout(blurTid);
            select(i, $(this));
            e.preventDefault();
        });
        
        // навигация мышкой
        body.on('mouseenter', selectorLi, function(e){
            let i = $(selectorPopup).data('input');
            let o = i.data('alexSuggest');
            $(selectorPopup + ' .' + o.hoverClass).removeClass(o.hoverClass);
            $(this).addClass(o.hoverClass);
            o.onSelectionChange(i, this);
        });

    }

})();
