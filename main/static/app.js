$(function(){



	$(function(){

        alexSuggest('input.test', {
            url: '/api/suggest',
            uniquePart: 'data-id',
            inputOffsetTop: 20,
            inputOffsetLeft: 0,
            inputOffsetWidth: 24,
            autoValueText: true, 
            onSelect: function(i, e){
                content = e.attr('data-id');
            },
        });

	});







});
