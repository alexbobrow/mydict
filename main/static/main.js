$(function(){

	var aud = $('audio')[0];

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


	$('body').on('click', 'button[data-action=pronounce]', function(e){
		aud.src = $(this).attr('data-url');
	});

	$('body').on('click', '.words-row span.hover', function(e){
		var col = $(this).closest('.translation');
		var i = col.find('input[type=text]');
		setEditStatus(col, 'edit');
		i[0].selectionStart = i[0].selectionStart = i.val().length;
		i.focus();
	});


	function setEditStatus(col, status) {
		col.removeClass('idle');
		col.removeClass('edit');
		col.addClass(status);
	}


	$('body').on('submit', '.edit-translation form', function(e){
		e.preventDefault();
		var col = $(this).closest('.translation');
		var input = col.find('input[name=translation]');
		var data = $(this).serializeArray();
		setEditStatus(col, 'idle');
		$.post(appUrls.update, data, function(ans){
			col.find('span.hover').text(input.val());
			col.addClass('custom');
		}, 'json');

	});



	$('body').on('click', 'button[data-action=translation-cancel]', function(e){
		e.preventDefault();
		var col = $(this).closest('.translation');
		setEditStatus(col, 'idle');
	});


	$('body').on('click', 'button[data-action=translation-reset]', function(e){
		e.preventDefault();
		var col = $(this).closest('.translation');
		var id = col.find('input[name=word_id]').val();
		setEditStatus(col, 'idle');

		$.post(appUrls.reset, {word_id: id}, function(ans){
			col.find('span.hover').text(ans.translation);
			col.find('input[name=translation]').val(ans.translation);
			col.removeClass('custom');
		}, 'json');



	});

	


}); // dom ready