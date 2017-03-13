$(function(){




	$('body').on('click', 'button.open-menu', function(){
		$('div.body').addClass('desktop-menu');
	});


	$('body').on('click', 'button.close-menu', function(){
		$('div.body').removeClass('desktop-menu');
	});


});