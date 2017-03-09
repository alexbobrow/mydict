$(function(){

    // vars

	
	$('body').on('click', 'button[data-action=add-to-dict]', function(e){
		alert('added');
	});


	$('body').on('click', 'button[data-action=remove-from-dict]', function(e){
		alert('removed');
	});



}); // dom ready