
var vocabListHTML = '<div id="vocablist" class="centred"></div>';
var crumbsHTML = '<div id="crumbs" class="centred"><span class="arrow">&#9658;</span></div>';
var singleWordHTML = '<div id="single"><div id="chars"></div><div class="line"><div class="pinyin"></div><div class="meaning"></div></div></div>';



    // LOADS AN HTML SNIPPET BASED ON A CLICK ACTION
    function loadContent() {
        $('.ajax, .wrapper, #crumbs a, a.single').click( function(e) {
            $('#loading').show();
            $('#header.home').removeClass('home');
            
            $('#head, h1.centred, #url').hide();
            if ($('#header').css('top') != 0) {
                $('#header').animate({'top':'0px',}, 300);
            };
            
            newURL = $(this).attr('href');
            $('.ajax, .wrapper, #crumbs a, a.single').unbind();
            loadPage(newURL);
            history.pushState('', '', newURL);
            e.preventDefault();
        });
        
        window.onpopstate = function(event) {
    	   if ( $('#header').hasClass('home') ) {
                $('#header').removeClass('home');   
           }
    	   $("#loading").show();
    	   
    	   loadPage(location.pathname);
	    }
        
    }
    
    // BINDS VARIOUS ELEMENTS TO THE AJAXY LOADCONTENT ABOVE
    function bindLoadContent() {
       $('.ajax, .wrapper, #crumbs a, a.single').unbind();
       loadContent();
    }
    
    
    // LOADS A PAGE BASED SOLELY ON A URL
    function loadPage(url) {
        
        $.ajax({
           url: url,
           dataType: 'json',
           success: function(data) {
              $('#container').html(data.html);
              $('#loading').hide();
              bindLoadContent();
              bindWords();
           } 
        });
    }
    
    // SEARCH VIA URL
    function searchByURL(e) {
        $.ajax({
           url: $(this).attr('href'),
           dataType: 'json',
           success: function(data) {
               history.pushState('', 'title', data.url);
               $('#container').html(data.html);
           }
        });   
    }

    // THE POST SEARCH FORM
    function searchSubmit(e) {
       $('#loading').show();
       $('#header.home').removeClass('home');
       
       if ($('#id_char').val()!='') {
            $.ajax({ 
                url: $('#search').attr('action'),
                type: 'POST',
                data: $('form').serialize(),
                dataType: 'json',
                success: function(data) {   
                    history.pushState('', 'title', data.url);
                    $('#container').html(data.html);
                    bindLoadContent(); 
                    bindWords();
                    $('#loading').hide();
                }, error: function() {
                    $('#text').html('<p>There was some kind of error, please try again!</p>');
                    $('#loading').hide();
                }
            });
            return false;
         } else {
             // HANDLE AN EMPTY SEARCH
             if ($('#search-error').length) {
                $('#search-error').fadeIn(100);   
             } else {
                $('#header').append('<p id="search-error">You need to enter some words to search for!</p>');
             };
             $('#search-error').css('color', 'red').delay(1800).fadeOut(400);
             $('#id_char').focus();
             $('#loading').hide(); 
             return false;
         }
    } 
    
    
    
    
    // GET'S A USERS PERSONAL VOCABULARY LIST
    function getPersonalWords() {
        $('#container').html('');
        $.ajax({ 
            url: '/get-personal-words/',
            type: 'GET',
            dataType: 'json',
            success: function(data) {            
                $('#container').html(vocabListHTML).prepend(crumbsHTML);
                $('#crumbs').append('<a href="/vocab/">Your Vocabulary</a>');
                arrayDict(data);
            },
        });
        return false;   
    }
    
   




// BINDS SINGLE WORDS SO THAT THEY CAN BE SEARCHED ON
function bindSingleWords() {
   $('.single').bind('click', getSingleWord);   
}

// HELPER FUNCTIONS 

function slideLeft(element) {
  element.animate({left: '-10000px'}, 200).fadeOut(100);    
}

function findPos(obj) {
	var curleft = curtop = 0;
	if (obj.offsetParent) {	
		do {
			curleft += obj.offsetLeft;
			curtop += obj.offsetTop;	
		} while (obj = obj.offsetParent);
	}
	return [curleft,curtop];
}

function trim(str) {
    return str.replace(/^\s*|\s*$/g,"");
}

function findChineseChars() {
    
    $('#text').search();
    var re1 = new RegExp("^[\u4E00-\uFA29]*$"); //Chinese character range
    var re2 = new RegExp("^[\uE7C7-\uE7F3]*$"); //Chinese character range
    str = str.replace(/(^\s*)|(\s*$)/g,'');
    if (str == '') {
        alert("Oh, man, Please input Chinese character.");
        return;
    }
    
    if (!(re1.test(str) && (! re2.test(str)))) {
        alert("Oops, Please input Chinese character.");
        return;
    }
}

function clearInput() {		
	$('.clearMeFocus').each( function() {
	   if ($(this).val() == '') {
	      var id = $(this).attr('id');
	      $('label[for="'+id+'"]').show();
	   }
	});
	
	$('.clearMeFocus').focus(function() {	
		var id = $(this).attr('id');
		$('label[for="'+id+'"]').addClass('focus');
	});
	
	// if field is empty afterward, add text again
	$('.clearMeFocus').blur(function() {
		var id = $(this).attr('id');
		
		if($(this).val()=='') {
			$('label[for="'+id+'"]').removeClass('focus');
		}
	}); 
	
	$('.clearMeFocus').keyup( function() {
	    var id = $(this).attr('id');
	    if ($(this).val() != '') {
		  $('label[for="'+id+'"]').hide();
	    } else {
	      $('label[for="'+id+'"]').show();
	    }
	});  
}
    


