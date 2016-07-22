(function(){

    /*
    
    alexSuggest

    Версия 4.1
    bug fices on plain enter old code garbage    

    Версия 4.0

    Все переделано с объектного стиля в обычный, так как объект относится к вызову а не инпуту
    что вызывает массу путаницы

    data-id больше не обязательное поле, уникальность проверяется по дополнительному параметру
    uniquePart

    добавлен параметр ignoreRepeat

    добавлена блокировака отправки формы при нажатии на интер по инпуту

    параметр autoValueAttr теперь массив, что позволяет установить любой атрибут
    а не только data-id как раньше

    новый алгоритм позволяет легко изменять ллюбые параметры индивидуально по каждому инпуту

    по-прежнему уникальная фишка в том, что прекрасно работают новые динамически созданные поля

    ожидаемый контент переделан в html вместо xml

    навигационные элементы переделаны в li вместо a

    */

    /* global */

    var popupId = 'alsuli'
    var selectorPopup = '#' + popupId;
    var selectorLi = selectorPopup + " li";

    var queryTid = 0;
    var blurTid = 0;


    window.alexSuggest = function(selector, params){


        createContainer();


        var defaultParams = {
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


    
        $('body').on('click', selector, function(e){
            $(this).keyup();
            e.stopPropagation();
        });


        $('body').on('blur', selector, function(e){
            var i = $(this);
            // при клике на попап без блюра все портится
            blurTid = setTimeout(function(){
                cancel(i);
            }, 200);          
        });


        // блокировка отрпавки формы
        $('body').on('keypress', selector, function(e){
            var code = (e.charCode)? e.charCode : e.keyCode;
            if (code == 13) {
                e.preventDefault();
                e.stopPropagation();
            }

        });


        $('body').on('keyup', selector, function(e){

            var o = getObject(params, defaultParams, this);
            var i = $(this);
            
            clearTimeout(queryTid);
            
            var code = (e.charCode)? e.charCode : e.keyCode;

            
            if (code == 38) {
                up(i);
                return true;
            }       
            
            if (code == 40) {
                down(i);
                return true;
            }
            
            if (code == 13) {
                enter(i);
                e.preventDefault();
                e.stopPropagation();
                return false;
            }       
            
            // далее обработка нажатия любой другой клавиши, предлположительно новая буква
            
            queryTid = setTimeout(function(){
                o.onQueryBefore(i);
                o.postParams.value = i.val();
                $.get(o.url, o.postParams, function(data){
                    o.onQueryAfter(i);
                    showPopup(i, data);
                }, 'html');
            },300);
        
        });


        $(selector).each(function(e){
            var o = getObject(params, defaultParams, this);
        });        


    } // w.as


    function getObject(defaultParams, params, input) {
        i = $(input);

        if (typeof(i.data('alexSuggest'))=='undefined') {

            var o = $.extend({}, params, defaultParams);
            i.data('alexSuggest', o);
            o.initialValue = i.val();
            return o;

        } else {
            return i.data('alexSuggest');
        }

    }





    function up(i){

       
        if (!$(selectorPopup).length) return;

        
        
        var length = $(selectorLi).length;
        if (length<1) return;

        var o = i.data('alexSuggest');       
        var selectorHover = selectorLi + '.' + o.hoverClass        

        
        var index = $(selectorLi).index($(selectorHover));
        var new_index = (index-1) ;

        if (new_index<0) { new_index = (length-1); }

        $(selectorHover).removeClass(o.hoverClass);
        
        var newSelected = $(selectorLi + ":eq("+new_index+")");
        newSelected.addClass(o.hoverClass);
        
        o.onSelectionChange(i, newSelected);
        
        return; 
    }



    function down(i) {

        if (!$(selectorPopup).length) return;

        
        var length = $(selectorLi).length;
        if (length<1) return;

        var o = i.data('alexSuggest');       
        var selectorHover = selectorLi + '.' + o.hoverClass        

        
        var index = $(selectorLi).index($(selectorHover));
        var new_index = index;

        if (new_index<0) {
            new_index = 0;
        } else {
            new_index++;
            if (new_index==length) {
                new_index = 0;
            }
        }


        $(selectorHover).removeClass(o.hoverClass);
        
        var newSelected = $(selectorLi + ":eq("+new_index+")");
        newSelected.addClass(o.hoverClass);
        
        o.onSelectionChange(i, newSelected);
        
        return; 

    }




    /**
     * при нажатии на интер по полю
     */
    function enter(i) {
        
        var o = i.data('alexSuggest');
        
        var jElem = $(selectorPopup + " ." + o.hoverClass);
        
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

        o = i.data('alexSuggest');

        var unique = getUniqueValue(i, li);
        if (unique &&  o.ignoreRepeat && o.processedUnique && o.processedUnique==unique) {
            $(selectorPopup).empty().hide();
            return false;
        }

        if (o.autoValueText) {
            i.val(li.text());
        }
        
        if (o.autoValueAttr!==null) {
            var autoInput = o.autoValueAttr[0]; 
            var attrName = o.autoValueAttr[1];
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
        o = i.data('alexSuggest');
        o.onCancel(i);
        $(selectorPopup).empty().hide();
    }




    function getUniqueValue(i, li) {
        o = i.data('alexSuggest');
        if (o.uniquePart) {
            if (o.uniquePart=='text()') {
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

        var o = i.data('alexSuggest');

        var popupOffset = i.offset();
        
        $(selectorPopup).css({
            top: (popupOffset.top + i.height() + o.inputOffsetTop) + "px",
            left: (popupOffset.left + o.inputOffsetLeft) + "px",
            width: (i.width() + o.inputOffsetWidth) + "px"
        });

        $(selectorPopup).html(data);

        if (o.setClass!='') {
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
        
        var unique = null;
        
        // отметим ранее выбранный, если актуально
        $(selectorLi).each(function(){           
            var unique = getUniqueValue(i, $(this));
            if (unique == o.processedUnique) {
                $(this).addClass(o.hoverClass);
            }
        });
        
    }




    function createContainer() {

        if ($(selectorPopup).length) {
            $(selectorPopup).empty();
            return;
        }

        $("body").append($("<div id='"+popupId+"' style='display:none'></div>").hover(function(){ $(this).addClass("hover"); },function(){ $(this).removeClass("hover"); }));

        $('body').on('click', selectorLi, function(e){
            var i = $(selectorPopup).data('input');
            clearTimeout(blurTid);
            select(i, $(this));
            e.preventDefault();
        });
        
        // навигация мышкой
        $('body').on('mouseenter', selectorLi, function(e){
            var i = $(selectorPopup).data('input');
            var o = i.data('alexSuggest');
            $(selectorPopup + ' .' + o.hoverClass).removeClass(o.hoverClass);
            $(this).addClass(o.hoverClass);
            o.onSelectionChange(i, this);
        });

    }





 
})();


