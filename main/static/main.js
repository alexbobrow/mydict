$(function(){

	// init
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        },
        error: function(xhr, status, error){
            alert('При выполнении запроса произошла ошибка.\n'+ status + '\n' + error);
        },
    });	

    // vars

	
	$('body').on('click', 'button[data-action=add-to-dict]', function(e){
		var row = $(this).closest('.words-row');
		var wordId = row.attr('data-word-id');
		$.post(appUrls.add, {word_id: wordId}, function(ans){
			row.addClass('added');
		}, 'json');
	});


	$('body').on('click', 'button[data-action=remove-from-dict]', function(e){
		var row = $(this).closest('.words-row');
		var wordId = row.attr('data-word-id');
		$.post(appUrls.remove, {word_id: wordId}, function(ans){
			if (listType=='freq') {
				row.removeClass('added');
			}
			if (listType=='own') {
				row.fadeOut(500, function(){
					row.remove();
				});
			}
		}, 'json');
	});



}); // dom ready