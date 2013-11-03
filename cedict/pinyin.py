#!/usr/bin/python
# -*- coding: utf8 -*-

AMBIGUOUS_WORDS = [
u'a', # a book
u'an', # an item
u'ban', # ban a book
u'hang', # hang up
u'can', # can you sing?
u'sang', # he sang for glory
u'bin', # rubbish bin
u'che', # che guevara?
u'fan', # ceiling fan
u'long', # a long long time
u'men', # many men
u'man', # a man
u'song', # a song
u'run', # run run run
u'sun', # the big thing in the sky
u'pang', # pangs of guilt?
u'me', # itu's all about me
u'nu', # apparently it's the greek Νν as well as nu in pinyin
]


PINYIN_WORDS = [
u'a',
u'ai',
u'an',
u'ang',
u'ao',
u'ba',
u'ban',
u'bang',
u'bao',   
u'bo', 
u'bi',
u'bin',
u'bing',
u'bu',
u'ca',
u'can',
u'cang',
u'ce',
u'cha',
u'chan',
u'chang',
u'chao',
u'che',
u'chen',
u'cheng',
u'chong',
u'chuan',
u'chuang',
u'chun',
u'chi',
u'chu'
u'chun', 
u'ci',
u'cong',
u'cu',
u'cun',
u'da',
u'dan',
u'dang',
u'de',
u'deng',
u'di',
u'die',
u'dian',
u'ding',
u'dong',
u'dou',
u'du',
u'e',
u'en',
u'er',
u'fa',
u'fan',
u'fang',
u'fen',
u'feng',
u'gan',
u'gang',
u'ge'
u'gen',
u'geng',
u'gou',
u'gu',
u'gua',
u'gui',
u'guo',
u'ha',
u'hai',
u'han',
u'hang',
u'he',
u'hen',
u'heng',
u'hu',
u'hua',
u'huan',
u'huang',
u'ji',
u'jia',
u'jian',
u'jiang',
u'jie',
u'jin',
u'jing',
u'jiong',
u'jiu',
u'ju',
u'juan',
u'jun',
u'jue',
u'ka',
u'kan',
u'kang',
u'kong',
u'kua',
u'kuan',
u'kuang',
u'kun',
u'la',
u'lan',
u'lang',
u'li',
u'lian',
u'liang',
u'liu',
u'long',
u'lu',
u'lun',
u'lv',
u'ma',
u'man',
u'mang',
u'me',
u'men',
u'meng',
u'mi',
u'mian',
u'mie',
u'min',
u'ming',
u'mo',
u'mu',  
u'na',
u'nan',
u'ne',
u'nen',
u'ni',
u'nian',
u'niang',
u'nie',
u'niuu'
u'nu',
u'nü',
u'nv',  
u'o',
u'ou',
u'pa',
u'pan',
u'pang',
u'pei',
u'peng',
u'pian',
u'qi',
u'qian',
u'qiang',
u'qie',
u'qin',
u'qing',
u'qu',
u'ran',
u'rang',
u're',
u'ren',
u'reng',
u'rong',
u'ru',
u'run',
u'sa',
u'san',
u'sao',
u'sang',
u'se',
u'sen',
u'shan',
u'shao',
u'shang',
u'she',
u'shi',
u'shuang',
u'shun',
u'si',
u'song',
u'su',
u'suan',
u'suang',
u'sun',
u'ta',
u'tan',
u'tao',
u'tang',
u'te',
u'teng',
u'ti',
u'tian',
u'tie',
u'tong',
u'tou',
u'tun',
u'tuo', 
u'wa',
u'wan',
u'wang',
u'wen',
u'wo',
u'wu', 
u'xi',
u'xian',
u'xin',
u'xing',
u'xu',
u'xuan',
u'xue',
u'ya',
u'yan',
u'yang',
u'ye',
u'yi',
u'yin',
u'ying',
u'yong',
u'yu',
u'yuan',
u'yue',
u'za',
u'zang',
u'zao',
u'ze',
u'zen',
u'zeng',
u'zha',
u'zhan',
u'zhang',
u'zhao',
u'zhe',
u'zhen',
u'zheng',
u'zhun',
u'zhong',
u'zhua',
u'zhuan',
u'zhuang',
u'zi',
u'zu',
u'zun',
]