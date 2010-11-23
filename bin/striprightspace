#!/usr/bin/python

import os
import sys

for file in os.listdir(sys.argv[1]):
    if os.path.isdir(file):
        continue
    lines = open(file).read().split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line.rstrip())
    f = open(file,'w')
    f.write('\n'.join(new_lines))
    f.close()
