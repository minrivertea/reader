#!/usr/bin/python
# -*- coding: utf8 -*-

AMBIGUOUS_WORDS = [
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
]


PINYIN_WORDS = [
u'a',
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
u'ci',
u'cong',
u'cun',
u'da',
u'de',
u'ding',
u'dong',
u'du',
u'e',
u'en',
u'fa',
u'fan',
u'fang',
u'fen',
u'feng',
u'gan',
u'gang',
u'ha',
u'han',
u'hang',
u'jie',
u'jin',
u'jing',
u'ju',
u'jue',
u'ka',
u'kan',
u'kang',
u'kong',
u'kun',
u'la',
u'lan',
u'lang',
u'li',
u'lian',
u'liang',
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
u'shuang',
u'shun',
u'song',
u'su',
u'suan',
u'suang',
u'sun',
u'ta',
u'tan',
u'tang',
u'teng',
u'tong',
u'tun', 
u'wa',
u'wan',
u'wang',
u'wen',
u'wo',
u'wu', 
u'xi',
u'xin',
u'xing',
u'xu',
u'xuan',
u'xue',
u'ya',
u'yan',
u'yang',
u'ye',
u'yin',
u'ying',
u'yong',
u'yu',
u'yuan',
u'yue',
u'za',
u'zang',
u'zao',
u'zha',
u'zhan',
u'zhang',
u'zhao',
u'zhun',
u'zhong',
u'zhua',
u'zhuan',
u'zhuang',
u'zu',
u'zun',
]