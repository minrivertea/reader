/*
It's worth detailing how the page/content loading happens. 

Basically, we want everything to go through loadPage() via a normal GET URL. THere should be
various handlers that filter requests through (eg. if someone clicks on a normal <a> link, then
the loadLink() handler will convert the href into a URL. If someone submits a search, then 
the searchSubmit() handler will convert the search into a URL.

The 1st page loads, and it hits Django, which serves the full HTML/CSS/JS. From then on in:
    
    1. We catch any link clicks with loadLink()
    2. The loading spinner is shown.
    3. We get the relevant URL from the href attr of the item that was clicked
    4. We get the HTML via loadPage()
    5. We add the new URL to the browser history (so that users can click 'back')

If someone just uses back/forward then it jumps directly to the loadPage() function.

*/


var vocabListHTML = '<div id="vocablist" class="centred"></div>';
var crumbsHTML = '<div id="crumbs" class="centred"><span class="arrow">&#9658;</span></div>';
var singleWordHTML = '<div id="single"><div id="chars"></div><div class="line"><div class="pinyin"></div><div class="meaning"></div></div></div>';

    function checkHeader() {
        if (window.location.pathname == '/') {
            $('#header').addClass('home');   
        } else {
           if ($('#header').hasClass('home')) {
             $('#header').removeClass('home');
           }   
        }
    }

    // HAPPENS WHEN A USER CLICKS A LINK
    function loadLink() {
        $('.ajax, .wrapper, #crumbs a, a.single').click( function(e) {                        
            var newURL = $(this).attr('href');
            $('.ajax, .wrapper, #crumbs a, a.single').unbind();
            loadPage(newURL);
            return false;
        });
    }
    
    // BINDS VARIOUS ELEMENTS TO THE AJAXY loadLink ABOVE
    function bindLoadLink() {
       $('.ajax, .wrapper, #crumbs a, a.single').unbind();
       loadLink();
    }
    
    // LOADS A PAGE OF CONTENT WITH A URL
    function loadPage(url) {
        $('#loading').show();
        history.pushState('', '', url);
        $.ajax({
           url: url,
           dataType: 'json',
           success: function(data) {
              checkHeader();
              $('#container').html(data.html);
              $('#loading').hide();
              bindLoadLink();
              bindWords();
           }
        });
    }


    // THIS MANAGES THE BROWSER FORWARDS/BACK BEHAVIOUR
    window.onpopstate = function(event) {   
    	alert('This is the popstate URL: ' + location.pathname);
        loadPage(location.pathname);
	}
    
    // SEARCH VIA URL
    // function searchByURL(e) {
    //     $.ajax({
    //        url: $(this).attr('href'),
    //        dataType: 'json',
    //        success: function(data) {
    //            history.pushState('', 'title', data.url);
    //            $('#container').html(data.html);
    //        }
    //     });   
    // }

    // THE POST SEARCH FORM
    function searchSubmit(e) {
       
       // MAKE SURE THERE'S A SEARCH QUERY
       if ($('#id_char').val()!='') {
            
            var newURL = $('#search').attr('action') + $('#id_char').val() ;
            loadPage(newURL);
            return false;
            
       } else {
             // HANDLE AN EMPTY SEARCH
             $('#container').html('<p id="search-error" class="centred">You need to enter some words to search for!</p>');
             $('#search-error').css('color', 'red').delay(11800).fadeOut(400);
             $('#id_char').focus();
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
    


