
var vocabListHTML = '<div id="vocablist" class="centred"></div>';
var crumbsHTML = '<div id="crumbs" class="centred"><span class="arrow">&#9658;</span></div>';
var textHTML = '<div id="text" class="centred easy"></div>';
var textHeadHTML = '<div id="head" class="centred easy"><a id="original-page" title="" href="">Original page</a><div id="appearance" class="set"><span class="button">Fonts</span><div class="extra"><div><h4>Change font</h4><ul id="fonts"><li><a href="#" class="font1 selected" onclick="changeFont(&apos;font1&apos;, false);" title="KaiTi">汉字</a></li><li><a href="#" class="font2" onclick="changeFont(&apos;font2&apos;);" title="SongTi">汉字</a></li><li><a href="#" class="font3" onclick="changeFont(&apos;font3&apos;);" title="FangSong">汉字</a></li><li><a href="#" class="font4" onclick="changeFont(&apos;font4&apos;);" title="HeiTi">汉字</a></li></ul></div><div><h4>Theme</h4><ul id="colors"><li><a href="#" onclick="changeColor(&apos;color1&apos;);" class="color1" title="Red"></a></li><li><a href="#" onclick="changeColor(&apos;color2&apos;);" class="color2" title="blue"></a></li><li><a href="#" onclick="changeColor(&apos;color3&apos;);" class="color3" title="green"></a></li><li><a href="#" onclick="changeColor(&apos;color4&apos;);" class="color4" title="black"></a></li></ul></div></div></div><div id="group" class="set"><span class="button" class="">Group Words</span></div><div id="pinyin" class="set"><span class="button" class="selected">Pinyin</span></div></div><h1 class="centred"></h1><span id="url" class="centred"></span>';
var singleWordHTML = '<div id="single"><div id="chars"></div><div class="line"><div class="pinyin"></div><div class="meaning"></div></div></div>';


    
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


    // TOGGLE PINYIN DISPLAY 
    $('#pinyin').click(function() {
      if ($(this).hasClass('selected')) {
        $(this).removeClass('selected');
        $('#text').removeClass('pinyin');
        $('.word .pinyin').hide();
      } else {
        $(this).addClass('selected');
        $('#text').addClass('pinyin');
        $('.word .pinyin').show();
      }  
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
            $('#lookups #' + idToRemove).remove();
    
        } else {
            item.addClass('selected');
            $('#lookups').append('<div id="'+(item.attr("id"))+'">'+'<div class="extra"><p>Something will go in here about the definition of the word or whatever...</div><span class="title">'+item.attr('chars')+'</span><span class="pinyin">'+item.children('.pinyin').text()+'</span>'+item.attr('title')+'</div>');
            selectUBItem($('#lookups #'+item.attr("id")));
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
       $('#lookups div').removeClass('selected');
       $(this).addClass('selected');
    }
  });   
}

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




// USED TO BIND WORDS IN A LONG TEXT SO THAT THEY CAN BE SEARCHED
function bindWords() {
    $('.word').not('.english, .punctuation, .number').click( function(e) {
       if (e.shiftKey) {addEditableWord(this);}  
       else { toggleUBI($(this)); }
    });

    $('.word').hover( function(e) {
       $('#lookups div#'+this.id).css({'position': 'relative', 'left': '-10px', 'background': '#fff'}); 
    }, function() {
       $('#lookups div#'+this.id).attr('style', ' ');   
    });
}

