#!/usr/bin/env python

import os
import shutil

for file in os.listdir('.'):
    if file.endswith('.po'):
        target = file.split('-')[-1]
        os.system('mv %s %s' % (file, target))
