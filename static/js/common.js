
$('#pyonoff').click(function() {
   if ($(this).hasClass('selected')) {
      $('.pinyin').css('display', 'block');
      $(this).removeClass('selected');
   }
   else {
      $('.pinyin').css('display', 'None');
      $(this).addClass('selected');
   } 
});

$('#easy').click(function() {
   if ($(this).hasClass('selected')) {
      $('#text').removeClass('easy');
      $(this).removeClass('selected');
   }
   else {
      $('#text').addClass('easy');
      $(this).addClass('selected');
   } 
});

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

function addRemoveUserBlockItem(item) {
    if (item.hasClass('selected')) {
        item.removeClass('selected');
        var idToRemove = item.attr('id');
        $('#userblock #' + idToRemove).remove();
    } else {
        item.addClass('selected');
        $('#userblock').append('<div id="'+(item.attr("id"))+'">'+'<div class="extra"></div><span class="title">'+item.attr('chars')+'</span><br/>'+item.attr('title')+'</div>');
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


$('.word').click( function(e) {
   
   if (e.shiftKey) {
         addEditableWord($(this));     
   } else {
       addRemoveUserBlockItem($(this));
   }
});


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

