
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
  if ($('#header').css('top') != 0) {
      $('#header').animate({'top':'0px',}, 300);
  }
  $('#text').load(href);
  $('#loading').hide();
  return false;
}

$.ajaxStart( function() {
  $('#loading').show(); 
});

$.ajaxStop( function() {
   $('#loading').hide(); 
});



function submitForm(e) {
  var tS = $('#id_char').val();    
  if (pS == null) {pS = ' ';}
  if (tS.localeCompare(pS.toString()) != 0) {
        pS = tS;
        
        $('form, #header').animate({'top': '0px'}, 300);
        
        if ($('#id_char').val()=='') {
            $('#text').append('<p>You have to put in some Chinese characters to search - try these: 您好</p>');
        } else { 
                
            $.ajax({ 
            url: $('#id_char').attr('action'),
            type: 'POST',
            data: $('form').serialize(),
            dataType: 'json',
            success: function(data) {
                arrayWords(data);
                bindWords();
            },
            error: function() {
                $('#text').html('<p>There was some kind of error, please try again!</p>');
                $('#search').bind('submit', submitForm);
            }
            });
            return false;   
        }
      }
      return false; 
}


function getTextByUID(uid) {
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
            if (v.character == ' ' || v.is_punctuation == true) return;
            if (v.is_english == true) return;
            if (v.wordset==tWS) {
              var wID = v.wordset + "";
                $('#text td#char'+wID).append(v.character);
                $('#text td#pinyin'+wID).append(' '+v.pinyin);
            } else {
              tWS = v.wordset;
              var html = '<tr><td id="char'+v.wordset+'">'+v.character
              html += '</td><td class="pinyin" id="pinyin'+v.wordset+'">'+v.pinyin+'</td><td>'+v.meaning+'</td></tr>';
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
            
            if (v.character == ' ') return;
            if (v.is_linebreak == true) { $('#text').append('<br clear="all"/><br clear="all"/>')};
            if (v.is_punctuation == true) wC += ' punctuation';
            if (v.is_number== true) wC+=' number';
            if (v.is_english==true) wC +=' english';
            
            var wW = '<div class="word'+wC+'" id="word'+v.wordset+'" chars="'+v.character+'" title="'+v.meaning+'" pinyin="'+v.pinyin+' ">';
            
            var html = '<div id="'+k+'" class="char" rel="'+v.wordset+'">';
            html+='<span class="hanzi">'+v.character+'</span>';
            if (v.pinyin) html+='<span class="pinyin">'+v.pinyin+'</span>';
            html+='</div>';
            
            if (v.wordset==tWS) {
                $('#text #word'+v.wordset).append(html);
                var newChars = ($('#text #word'+v.wordset).attr('chars') + v.character);
                var newPY = ($('#text #word'+v.wordset).attr('pinyin') + v.pinyin);
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


var counter = 0
$('.char').not('.punctuation').each(function(index) {
   
   var curr = $(this).attr('rel');   
   allChars = '';

   $('.char[rel="'+curr+'"]').each( function() {
      allChars += ($(this).find('.hanzi').html());
   });
   
   if ($(this).parent().hasClass('word')) {
       $(this).attr('id', '');
   } 
   else {
        $('.char[rel="'+curr+'"]').wrapAll('<div class="word" chars="'+allChars+'" id="'+counter+'" title="'+($(this).attr('title'))+'" />');
        $(this).attr('id', '');
        counter ++; 
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
        counter += 1;
        selectUBItem($('#userblock #'+item.attr("id")));
    };
}

function removeEditBlock() {
  $('#userblock .editing').remove();   
}


function addEditableWord(item) {
    if (item.hasClass('select')) {
        item.removeClass('select');
        var editBlock = $('#userblock .editing .editable');
        editBlock.text(editBlock.text().replace(item.attr('chars'), ''));
        if (editBlock.text().length < 1) {
            removeEditBlock();
        }
    } else {
        item.addClass('select');
        if ($('#userblock .editing')[0]) {
            $('#userblock .editing span.editable').append(item.attr('chars'));
        } else {
            $('#userblock').append('<div id="'+(item.attr("id"))+'" class="editing">'+'<span class="editable">'+item.attr('chars')+'</span><br/><input type="text" class="clearMeFocus" title="Write a note..." value=""/></div>');
            $('#userblock .editing input').bind('focus', clearInput());
        }
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
    $('.word').click( function(e) {
       if (e.shiftKey) { addEditableWord($(this));} else { toggleUBI($(this)); }
    });
    
    $('.word').hover( function(e) {
       $('#userblock div#'+this.id).css({'position': 'relative', 'left': '-10px', 'color': '#C33636'}); 
    }, function() {
       $('#userblock div#'+this.id).attr('style', ' ');   
    });
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

