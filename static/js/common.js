

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
        $('#userblock').append('<div id="'+(item.attr("id"))+'">'+'<div class="extra"><p>Something will go in here about the definition of the word or whatever...</div><span class="title">'+item.attr('chars')+'</span><br/>'+item.attr('title')+'</div>');
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
       $('#userblock div#'+this.id).css({'position': 'relative', 'left': '-10px', 'width': '210px', 'color': '#C33636'}); 
    }, function() {
       $('#userblock div#'+this.id).attr('style', ' ');   
    });
}


function clearInput() {
		// clear input on focus
		var clearMePrevious = '';
		
		$('.clearMeFocus').each( function() {
			if ($(this).val() == '') {
			    var title = $(this).attr('title');
			    $(this).val(title);
			}
		});
		
		$('.clearMeFocus').focus(function()
		{
			if($(this).val()==$(this).attr('title'))
			{
				clearMePrevious = $(this).val();
				$(this).val('');
				$(this).css('color', '#333');
			}
		});
		
		// if field is empty afterward, add text again
		$('.clearMeFocus').blur(function()
		{
			if($(this).val()=='')
			{
				$(this).val(clearMePrevious);
				$(this).css('color', '#999');
			}
		});   
}

