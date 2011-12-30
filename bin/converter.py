#!/usr/bin/python

import os
import glob

to_converted = glob.glob('*.JPG')
to_converted.sort()

print("Please enter the prefix: %s")
prefix = raw_input()

if not os.path.exists(prefix):
    os.makedirs(prefix)

for i, name in enumerate(to_converted):
    print('convert -resize 550x413 %s %s/%s-%d.jpg' % (name, prefix, prefix, i))
    os.system('convert -resize 550x413 %s %s/%s-%d.jpg' % (name, prefix, prefix, i))
