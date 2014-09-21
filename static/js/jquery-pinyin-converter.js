(function($) {

    // Start the plugin code
    $.fn.pinyin = function(parameter) {
    
        // The element reference
        var element = $(this);
        
        // Asterisks determine the position of the accent in pīnyīn vowel clusters
        var accentsMap = {
            iao: 'ia*o', uai: 'ua*i',
            ai: 'a*i', ao: 'a*o', ei: 'e*i', ia: 'ia*',  ie: 'ie*',
            io: 'io*', iu: 'iu*', Ai: 'A*i', Ao: 'A*o', Ei: 'E*i',
            ou: 'o*u', ua: 'ua*',  ue: 'ue*', ui: 'ui*', uo: 'uo*',
            ve: 'üe*', Ou: 'O*u', 
            a: 'a*', e: 'e*', i: 'i*', o: 'o*', u: 'u*', v: 'v*',
            A: 'A*', E: 'E*', O: 'O*'
        };        
        
        // Vowels to replace with their accented froms
        var vowels = ['a*','e*','i*','o*','u*','v*','A*','E*','O*'];
        
        // Accented characters for each of the four tones
        var pinyin = {
            1: ['ā','ē','ī','ō','ū','ǖ','Ā','Ē','Ī','Ō'],
            2: ['á','é','í','ó','ú','ǘ','Á','É','Í','Ó'],
            3: ['ǎ','ě','ǐ','ǒ','ǔ','ǚ','Ǎ','Ě','Ǐ','Ǒ'],
            4: ['à','è','ì','ò','ù','ǜ','À','È','Ì','Ò']
        };
        
        // The replacer function
        var pinyinReplace = function(match) {
        
            // Extract the tone number from the match
            var toneNumber = match.substr(-1, 1);
            
            // Extract just the syllable
            var word = match.substring(0, match.indexOf(toneNumber));
            
            // Put an asterisk inside of the first found vowel cluster
            for (var val in accentsMap) {
                if (word.search(val) != -1) {
                    word = word.replace(new RegExp(val), accentsMap[val])
                    break;
                }
            }
          
            // Replace the asterisk’d vowel with an accented character          
            for (i=0; i<10; i++)
                word = word.replace(vowels[i], pinyin[toneNumber][i]);
            
            // Return the result
            return word;
            
        }
    
        // Plugin initialisation
        var init = function() {
            
            // Bind a function to the keyup event for the attached element
            element.bind('keyup', function(e) {
            
                // Get the pressed key code
                var code = (e.keyCode ? e.keyCode : e.which);
                
                // Do stuff if it’s a space or one of the tone numbers (1-4)
                if (code == 32 || code == 49 || code == 50 || code == 51 || code == 52) {
                
                    // Get the value of the field
                    var inputText = $(this).val();
                    
                    // Run the replacer function for each numeric pīnyīn string match
                    inputText = inputText.replace(/([a-zA-Z]+)([1-5])/g, pinyinReplace);
                    
                    // Update the text field value
                    $(this).val(inputText);
                    
                } 
                
            });
            
        };
        
        init();
        
    }
        
})(jQuery);



function PinyinJs(){this.pinyinChars={1:"\u0101,\u0113,\u012b,\u014d,\u016b,\u01d6,\u0100,\u0112,\u012a,\u014c".split(","),2:"\u00e1,\u00e9,\u00ed,\u00f3,\u00fa,\u01d8,\u00c1,\u00c9,\u00cd,\u00d3".split(","),3:"\u01ce,\u011b,\u01d0,\u01d2,\u01d4,\u01da,\u01cd,\u011a,\u01cf,\u01d1".split(","),4:"\u00e0,\u00e8,\u00ec,\u00f2,\u00f9,\u01dc,\u00c0,\u00c8,\u00cc,\u00d2".split(",")};this.tonelessChars="a,e,i,o,u,\u00fc,A,E,I,O".split(",");this.accentsMap={iao:"ia*o",uai:"ua*i",ai:"a*i",ao:"a*o",ei:"e*i",
ia:"ia*",ie:"ie*",io:"io*",iu:"iu*",Ai:"A*i",Ao:"A*o",Ei:"E*i",ou:"o*u",ua:"ua*",ue:"ue*",ui:"ui*",uo:"uo*",ve:"\u00fce*",Ou:"O*u",a:"a*",e:"e*",i:"i*",o:"o*",u:"u*",v:"v*",A:"A*",E:"E*",O:"O*"};this.vowels="a*,e*,i*,o*,u*,v*,A*,E*,O*".split(",");this.makeObject=false;this.convert=function(a,f){var e=this,c=function(a){var b=a.substr(-1,1),d=!parseInt(b)?a:a.substring(0,a.indexOf(b));if(b==0||b>4||!parseInt(b))return f?{tone:5,syllable:d,originalSyllable:a}:d;for(var c in e.accentsMap)if(d.search(c)!=
-1){d=d.replace(RegExp(c),e.accentsMap[c]);break}for(i=0;i<10;i++)d=d.replace(e.vowels[i],e.pinyinChars[b][i]);return f?{tone:b,syllable:d,originalSyllable:a}:d};if(f){var b=[],a=a.replace(/([a-zA-Z\u00fc\u00dc]+)([\d])([^ ])/g,"$1$2 $3"),g=a.split(" "),h=g.length;for(j=0;j<h;j++)b.push(c(g[j]))}else a=a.replace(/([a-zA-Z\u00fc\u00dc]+)(\d)/g,c);return f?b:a};this.revert=function(a){var a=a.split(" "),f=a.length,e=[];for(j=0;j<f;j++){var c=0,b=a[j];for(i=1;i<5;i++)if(c==0)for(var g in this.pinyinChars[i]){if(b.search(this.pinyinChars[i][g])!=
-1){b=b.replace(RegExp(this.pinyinChars[i][g]),this.tonelessChars[g]);c=i;e.push({tone:c,syllable:b,originalSyllable:a[j]});break}}else break;c==0&&e.push({tone:5,syllable:b,originalSyllable:a[j]})}return e}}var pinyinJs=new PinyinJs;