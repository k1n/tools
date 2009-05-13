#!/usr/bin/python

import csv
import sys

LANG = {
    'English': 'en',
    'Nederlands': 'nl',
    'Italian': 'it',
    'Spanish': 'es',
    'Korean': 'ko',
    'Portuguese': 'pt',
    'Arabic': 'ar',
    'Russian': 'ru',
    'Portuguese (Br)': 'pt_BR',
    'Swedish': 'sv_SE',
    'Norwegian': 'nb',
    'Finnish': 'fi_FI',
    'Danish': 'da',
    'Polish': 'pl',
    'Hebrew': 'he',
    'Hungarian': 'hu',
    'Slovenian': 'sl_SI',
    'Greek': 'el',
    'Czech': 'cs_CZ',
    'Slovak': 'sk',
    'Turkish': 'tr',
    'Croatian': 'hr',
    'French': 'fr',
    'German': 'de',
    'Japanese': 'ja',
    'Simplified Chinese': 'zh_CN',
    'Traditional Chinese': 'zh_TW',
}

def build_translation_dict(file):
    reader = csv.DictReader(open(file))
    dict = [l for l in reader][0]
    new = {}
    for k,v in dict.items():
        if k in LANG.keys():
            new[LANG[k]] = v
    return new

if __name__ == '__main__':
   dict = build_translation_dict(sys.argv[1])

   for k, v in dict.items():
       print k,v
