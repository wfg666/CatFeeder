#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import shutil
import sys
import cv2

if len(sys.argv) < 2:
    print("Usage: python random_show.py <folder-path>")
    sys.exit()

# 定义常量
DATA_DIR = sys.argv[1]

png_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".png")]

random.shuffle(png_files)

for filename in png_files:
    img = cv2.imread(os.path.join(DATA_DIR, filename))
    cv2.imshow('image', img)
    key = cv2.waitKey(100)
    
    # if the escape key is pressed, the app will stop
    if key%256 == 27:
        print('escape hit, closing the app')
        break
