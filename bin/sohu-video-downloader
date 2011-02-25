#!/usr/bin/env python
# coding: utf-8
#
# Copyright(R) 2010 Tualatrix Chou <tualatrix@gmail.com>
# http://imtx.me
#
# The easiest way to download videos from sohu.com

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import os
import optparse
import urllib
import json

def get_vid_and_pid(url):
    vid_pattern = re.compile('var vid="(\d+)"')
    pid_pattern = re.compile('var pid ="(\d+)"')

    print("Try to get vid and pid...")
    html = urllib.urlopen(url).read()
    return vid_pattern.findall(html)[0], pid_pattern.findall(html)[0]

def get_video_file(vid, pid, hd=False):
    if hd:
        url = 'http://hot.vrs.sohu.com/vrs_flash.action?vid=%s&pid=%s' % (vid, pid)
    else:
        url = 'http://hot.vrs.sohu.com/vrs_flash.action?vid=%s&pid=%s?ver==1' % (vid, pid)
    json_data = json.loads(urllib.urlopen(url).read())
    tv_name = json_data['data']['tvName']

    for num, video_url in enumerate(json_data['data']['clipsURL']):
        basename = os.path.basename(video_url)
        if '?' in basename:
            basename = basename.split('?')[0]
        os.system('wget %s' % video_url)
        os.system('mv -v %s* %s' % (basename, tv_name + '-0%d.mp4' % (num + 1)))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: %s [url1 url2 ...] -g' % sys.argv[0])
        sys.exit(1)

    parser = optparse.OptionParser(prog="sohu-video-downloader",
                                   description="")
    parser.add_option("-l", "--low", action="store_true", default=False,
                      help="Download low quailty video.  [default: %default]")
    options, args = parser.parse_args()

    if options.low:
        ENABLE_HD = False
    else:
        ENABLE_HD = True

    for url in sys.argv[1:]:
        if url.startswith('http'):
            vid, pid = get_vid_and_pid(url)
            get_video_file(vid, pid, ENABLE_HD)
