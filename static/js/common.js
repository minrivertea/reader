
var vocabListHTML = '<div id="vocablist" class="centred"></div>';
var crumbsHTML = '<div id="crumbs" class="centred"><span class="arrow">&#9658;</span></div>';
var textHTML = '<div id="text" class="centred easy"></div>';
var textHeadHTML = '<div id="head" class="centred easy"><a id="original-page" title="" href="">Original page</a><div id="appearance" class="set"><span class="button">Fonts</span><div class="extra"><div><h4>Change font</h4><ul id="fonts"><li><a href="#" class="font1 selected" onclick="changeFont(&apos;font1&apos;, false);" title="KaiTi">汉字</a></li><li><a href="#" class="font2" onclick="changeFont(&apos;font2&apos;);" title="SongTi">汉字</a></li><li><a href="#" class="font3" onclick="changeFont(&apos;font3&apos;);" title="FangSong">汉字</a></li><li><a href="#" class="font4" onclick="changeFont(&apos;font4&apos;);" title="HeiTi">汉字</a></li></ul></div><div><h4>Theme</h4><ul id="colors"><li><a href="#" onclick="changeColor(&apos;color1&apos;);" class="color1" title="Red"></a></li><li><a href="#" onclick="changeColor(&apos;color2&apos;);" class="color2" title="blue"></a></li><li><a href="#" onclick="changeColor(&apos;color3&apos;);" class="color3" title="green"></a></li><li><a href="#" onclick="changeColor(&apos;color4&apos;);" class="color4" title="black"></a></li></ul></div></div></div><div id="group" class="set"><span class="button" class="">Group Words</span></div><div id="pinyin" class="set"><span class="button" class="selected">Pinyin</span></div></div><h1 class="centred"></h1><span id="url" class="centred"></span>';
var singleWordHTML = '<div id="single"><div id="chars"></div><div class="line"><div class="pinyin"></div><div class="meaning"></div></div></div>';



    // LOADS AN HTML SNIPPET BASED ON A CLICK ACTION
    function loadContent() {
        $('.ajax, .wrapper, #crumbs a, a.single').click( function(e) {
            $('#loading').show();
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
    	   $("#loading").show();
    	   console.log("pathname: "+location.pathname);
    	   loadPage(location.pathname);
	    }
        
    }
    
    // BINDS VARIOUS ELEMENTS TO THE AJAXY LOADCONTENT BELOW
    function bindLoadContent() {
       $('.ajax, .wrapper, #crumbs a, a.single').unbind();
       loadContent();
       bindWords();     
    }
    
    // LOADS A PAGE BASED SOLELY ON A URL
    function loadPage(url) {
        $('#container').load(url, function() {
            bindLoadContent();
            $('#loading').hide();    
        });    
    }
    
    
    // RETURNS A SINGLE CHARACTER OR WORD DEFINITION
    function getSingleWord(e, chars) {
        var crumbs = $('#crumbs')
        $('#container').html('');
        chars = chars || $('.chars', this).text().trim();
        $('#container').html(crumbs);
        history.pushState('', 'title', chars);            
        $.ajax({ 
            url: '/vocab/'+chars+'/',
            method: 'GET',
            data: chars,
            dataType: 'json',
            success: function(data) {
                $('#container').append(textHTML);
                $('#text').append(singleWordHTML);
                var chars = '';
                $(data).each( function(k,v) {
                    var newChars = v.chars.split('');
                    $(newChars).each( function(k,v) {
                       var newLink = location.pathname+v;
                       chars +=  '<a href="'+newLink+'" class="single"><span class="chars">'+v+'</span></a>';
                    });
                    $('.pinyin').append(v.pinyin1);
                    $('.meaning').append(v.meaning1);
                });
                $('#chars').html(chars);
                
                updateCrumbs();
                bindSingleWords();
                

            } 
        });
        return false;
    }

    // THE MAIN SEARCH FUNCTION
    var pS;
    function submitForm(e) {
       $('#loading').show();
       $('form, #header').animate({'top': '0px'}, 300);
       
       if ($('#id_char').val()!='') {

            var key, count = 0;
            
            for(key in ($('#id_char').val())) { count++; }
            if ( count < 10 ) {
                
                // HANDLE A SEARCH OF LESS THAN 10 CHARS
                var url = '/search/'+$('#id_char').val();
                loadPage(url);
                history.pushState('', '', url);
                return false;
            } else {
                
                // HANDLE A SEARCH OF MORE THAN 10 CHARS
                $.ajax({ 
                    url: $('#search').attr('action'),
                    type: 'POST',
                    data: $('form').serialize(),
                    dataType: 'json',
                    success: function(data) {   
                        history.pushState('', 'title', data.url);
                        $('#container').html(data.html);
                        bindWords();   
                        $('#loading').hide();
                    }, error: function() {
                        $('#text').html('<p>There was some kind of error, please try again!</p>');
                        $('#loading').hide();
                    }
                });
                return false;
            }
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
    
    // GETS EXAMPLES OF A CHARACTER/WORD IN USE FROM THE SERVER
    function getExamples(word) {
        $.ajax({
            url: '/get-examples/'+word+'/',
            dataType: 'html',
            success: function(data) {
                $('#container').append(data);
            },
            error: function() {
               alert('Failed to get examples!');  
            },
        });
        return false;   
    }

    // GETS A LONG TEXT BY A UID
    function getTextByUID(uid) {
       $('#container').html('');
       $('#container').html(textHeadHTML).prepend(crumbsHTML).append(textHTML);
       $('#crumbs').append('<a href="">Article</a>&nbsp;&nbsp;/&nbsp;&nbsp');
       $('#loading').show();
       $.ajax({ 
            url: '/url/'+uid+'/',
            type: 'GET',
            data: {'uid': uid},
            dataType: 'json',
            success: function(data) {
                arrayText(data);
                bindWords();
            }
       });
       $('#loading').hide();
       return false;
    }


// UI FUNCTIONS 


$('#pinyin').click(function() {
  if ($(this).hasClass('selected')) {
    $(this).removeClass('selected');
    $('.word .pinyin').hide();
  } else {
    $(this).addClass('selected');
    $('.word .pinyin').show();
  }  
});

function mySelect(item) {
   if ($(item).hasClass('selected')) {
      $(item).removeClass('selected');
   }
   else {
      $(item).addClass('selected');
   }  
}

$('#appearance .button').click(function() {
   mySelect($(this).parent());
});

$('#user').click(function() {
   mySelect(this);
});




    // CHANGES THE FONTS FOR LONG TEXTS
    function changeFont(fname) {
       $('#fonts a').removeClass('selected');
       $('#fonts .'+fname).addClass('selected');
       $('body').removeClass(function (index, fc) {
            var matches = fc.match (/font\d+/g) || [];
            return (matches.join (' '));
       }).addClass(fname);
       mySelect(this);
       return false;
    }
   
    // CHANGES THE COLORS FOR LONG TEXTS
    function changeColor(color) {
       $('#colors a').removeClass('selected');
       $('#colors .'+color).addClass('selected');
       $('body').removeClass(function (index, fc) {
            var matches = fc.match (/color\d+/g) || [];
            return (matches.join (' '));
       }).addClass(color);
       mySelect(this);
       return false;
    }

    // GROUP OR UNGROUP THE WORDS IN A LONG TEXT
    $('#group').click(function() {
       if ($(this).hasClass('selected')) {
          $('#text').removeClass('grouped');
          $(this).removeClass('selected');
       }
       else {
          $(this).addClass('selected');
          $('#text').addClass('grouped');
       } 
    });

    // ADDS OR REMOVES AN ITEM FROM THE USERBLOCK
    function toggleUBI(item) {
        if (item.hasClass('selected')) {
            item.removeClass('selected');
            var idToRemove = item.attr('id');
            $('#userblock #' + idToRemove).remove();
    
        } else {
            item.addClass('selected');
            $('#userblock').append('<div id="'+(item.attr("id"))+'">'+'<div class="extra"><p>Something will go in here about the definition of the word or whatever...</div><span class="title">'+item.attr('chars')+'</span><span class="pinyin">'+item.children('.pinyin').text()+'</span><br/>'+item.attr('title')+'</div>');
            selectUBItem($('#userblock #'+item.attr("id")));
        };
    }


function addEditableWord(item) {
    var pos = findPos(item);
       
    if ($(item).hasClass('selected')) {
        $(item).removeClass('selected');
        $('#editable div .chars').text($('#editable div .chars').text().replace($(item).attr('chars'), ''));
        $('#editable div .pinyin').text($('#editable div .pinyin').text().replace($(item).attr('pinyin'), ''));
        if ($('#editable div .chars').html() == '') {
           $('#editable div').remove();   
        }

    } else {
        $(item).addClass('selected');
        
        if ($('#editable div')[0]) {
            $('#editable div span.chars').append($(item).attr('chars'));
            $('#editable div span.pinyin').append($(item).attr('pinyin'));
        } 
        
        else {
            
            $('#editable').append('<div id="'+($(item).attr("id"))+'">'+'<span class="chars">'+$(item).attr('chars')+'</span><span class="pinyin">'+$(item).attr('pinyin')+'</span></div>');
            $('#editable div').append('<form action="" method="" id="editform"></form>');
            $('#editform').append('<label for="id_definition">Enter a definition</label><input name="definition" id="id_definition" type="text" class="clearMeFocus" title="Write your definition" value=""/><input type="submit" class="submit button" value="Save"/>');
             
            $('#'+$(item).attr('id')).css({'top': (pos[1]+60), 'left': (pos[0]-80)});
            
        }
      clearInput();
      $('#editable input[type=text]').focus();  
    };
}

function selectUBItem(item) {
  item.click(function() {
    if (item.hasClass('selected')) {
       $(this).removeClass('selected'); 
    } else {
       $('#userblock div').removeClass('selected');
       $(this).addClass('selected');
    }
  });   
}


// USED TO BIND WORDS IN A LONG TEXT SO THAT THEY CAN BE SEARCHED
function bindWords() {
    $('.word').not('.english, .punctuation, .number').click( function(e) {
       if (e.shiftKey) {addEditableWord(this);}  
       else { toggleUBI($(this)); }
    });


    $('.word').hover( function(e) {
       $('#userblock div#'+this.id).css({'position': 'relative', 'left': '-10px', 'color': '#C33636'}); 
    }, function() {
       $('#userblock div#'+this.id).attr('style', ' ');   
    });
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

function updateCrumbs() {
   // get the previous crumb and make it a link
   
   // add this item to the end.   
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
    


