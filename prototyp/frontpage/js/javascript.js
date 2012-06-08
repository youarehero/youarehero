// JavaScript Document
// Benedikt Morschheuser 2012 - info@BMo-design.de

$(document).ready(function () {
	//scrolling
	$.localScroll.defaults.axis = 'x';
	$.localScroll();
	//mousewheel
	if(!isTouchDevice()){
		$('html, body').mousewheel(function(event, delta) {
			this.scrollLeft -= (delta * 20);
			event.preventDefault();
		});
	}
	
	//PopUps
    //Sets up the modal
	var domModal = $("#domModal").modal({
	  backdrop: true, //Show a grey back drop
	  //closeOnEscape: true, //Can close on escape
	  modal: true //display it as a modal
	});
	domModal.modal('hide');

	$('.domModal-trigger').click(function (e) {
		e.preventDefault();
	    domModal.modal('toggle'); //Show the modal
		//content
		if($(this).attr('id')=="song_link"){
			$('#domModal-title').html('You are HERO - Someday');
			$('#domModal-body').html('<audio controls="controls"><source src="./files/SomedayYAH2.mp3" type="audio/mpeg" /><source src="./files/SomedayYAH2.ogg" type="audio/ogg" />Sorry, your browser does not support the html5 audio element.</audio>');
		}
		if($(this).attr('id')=="video_link"){
			$('#domModal-title').html('Tale of a Hero');
			$('#domModal-body').html('<iframe width="640" height="360" src="http://www.youtube.com/embed/7gp4X-0XSQA" frameborder="0" allowfullscreen></iframe>');
		}
		
	});

	$('#domModal .close').live('click', function(e){
		e.preventDefault();
	    domModal.modal('hide'); //Close the modal
		$('#domModal-body').empty();
	});
});

function isTouchDevice(){
	  return (typeof(window.ontouchstart) != 'undefined') ? true : false;
}