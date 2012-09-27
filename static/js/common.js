
$('#pinyin').click(function() {
  if ($(this).hasClass('selected')) {
    $(this).removeClass('selected');
    $('.pinyin').hide();
  } else {
    $(this).addClass('selected');
    $('.pinyin').show();
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

$('#header a.ajax').click( function(e) {  
  newURL = $(this).attr('href');
  loadContent(newURL);
  history.pushState('', 'title', newURL); 
  e.preventDefault();
});



function loadContent(href) {
  $('#loading').show();
  $('#head, h1.centred, #url').hide();
  if ($('#header').css('top') != 0) {
      $('#header').animate({'top':'0px',}, 300);
  };
  
  $('#text').load(href);
  eval($('#text').text());
  $('#loading').hide();
  return false;
}

var pS;
function submitForm(e) {
  var tS = $('#id_char').val();    
  if (pS == null) {pS = ' ';}
  if (tS.localeCompare(pS.toString()) != 0) {
        pS = tS;
        
        $('#loading').show();
        
        $('form, #header').animate({'top': '0px'}, 300);
        
        if ($('#id_char').val()=='') {
            $('#text').append('<p>You have to put in some Chinese characters to search - try these: 您好</p>');
            $('#loading').hide();
        } else { 
                
            $.ajax({ 
            url: $('#search').attr('action'),
            type: 'POST',
            data: $('form').serialize(),
            dataType: 'json',
            success: function(data) {
                arrayWords(data);
                bindWords();
                $('#loading').hide();
            },
            error: function() {
                $('#text').html('<p>There was some kind of error, please try again!</p>');
                $('#search').bind('submit', submitForm);
                $('#loading').hide();
            }
            });
            return false;   
        }
      }
      return false; 
}


function getTextByUID(uid) {
   $('#text').html('');
   $('#loading').show();
   if ($('#head').length) {
     $('#head, h1.centred, #url').show();
   }
   $.ajax({ 
        url: '/url/'+uid+'/',
        type: 'GET',
        data: {'uid': uid},
        dataType: 'json',
        success: function(data) {
            arrayWords(data);
            bindWords();
        }
   });
   $('#loading').hide();
   return false;
}


function arrayWords(data) {
    var key, count = 0;
    for(key in data) {
        count++;
    }

    if (count < 10) {
        var tWS;
        if ($('#text table').length) {
            $('#text table').prependTo('#previous-searches'); 
        }      
        $('#text').html('<table></table>');
        $(data).each( function(k,v) {
            if (v.chars == ' ' || v.is_punctuation == true) return;
            if (v.is_english == true) return;
            if (v.wordset==tWS) {
              var wID = v.wordset + "";
                $('#text td#char'+wID).append(v.chars);
                $('#text td#pinyin'+wID).append(' '+v.pinyin1);
            } else {
              tWS = v.wordset;
              var html = '<tr><td id="char'+v.wordset+'">'+v.chars
              html += '</td><td class="pinyin" id="pinyin'+v.wordset+'">'+v.pinyin1+'</td><td>'+v.meaning1+'</td></tr>';
              $('#text table').append(html);
            }
        });
    } else {
        $('#text').html('');
        $('#previous-searches').html('');
        $('#tools').fadeIn(500);
        var tWS;
        $(data).each( function(k,v) {
            var html;                
            var wC = '';
            
            if (v.chars == ' ') return;
            if (v.is_linebreak == true) { $('#text').append('<br clear="all"/><br clear="all"/>')};
            if (v.is_punctuation == true) wC += ' punctuation';
            if (v.is_number== true) wC+=' number';
            if (v.is_english==true) wC +=' english';
            
            var wW = '<div class="word'+wC+'" id="word'+v.wordset+'" chars="'+v.chars+'" title="'+v.meaning1+'" pinyin="'+v.pinyin1+' ">';
            
            var html = '<div id="'+k+'" class="char" rel="'+v.wordset+'">';
            html+='<span class="hanzi">'+v.chars+'</span>';
            if (v.pinyin1) html+='<span class="pinyin">'+v.pinyin1+'</span>';
            html+='</div>';
            
            if (v.wordset==tWS) {
                $('#text #word'+v.wordset).append(html);
                var newChars = ($('#text #word'+v.wordset).attr('chars') + v.chars);
                var newPY = ($('#text #word'+v.wordset).attr('pinyin') + v.pinyin1);
                $('#text #word'+v.wordset).attr('chars', newChars);
                $('#text #word'+v.wordset).attr('pinyin', newPY);
            } else {
                html+='</div>';
                var newHtml = wW+html;
                $('#text').append(newHtml);
                tWS = v.wordset;
            }
        });
    }  
}

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

function toggleUBI(item) {
    if (item.hasClass('selected')) {
        item.removeClass('selected');
        var idToRemove = item.attr('id');
        $('#userblock #' + idToRemove).remove();

    } else {
        item.addClass('selected');
        $('#userblock').append('<div id="'+(item.attr("id"))+'">'+'<div class="extra"><p>Something will go in here about the definition of the word or whatever...</div><span class="title">'+item.attr('chars')+'</span><span class="pinyin">'+item.attr('pinyin')+'</span><br/>'+item.attr('title')+'</div>');
        selectUBItem($('#userblock #'+item.attr("id")));
    };
}

function removeEditBlock() {
  $('#userblock .editing').remove();   
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

// not being used...
function expandUserBlock(item) {
    item.click( function() {
       $('#userblock').animate( {width: '650px'}, 400);
    });
}


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


function getPersonalWords() {
    $.ajax({ 
        url: '/get-personal-words/',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            $(data).each( function(k,v) {
               $('#session-searches').append('<p>'+v.chars+' / '+v.time+' / '+v.count+'</p>') 
            });
        },
        error: function() {
            $('#text').html('<p>There was some kind of error, please try again!</p>');
            $('#search').bind('submit', submitForm);
            $('#loading').hide();
        }
    });
    return false;   
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

