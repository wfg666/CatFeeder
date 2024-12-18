#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Generated by chatGPT

'''该脚本会遍历data目录下每个子目录，找到所有的png文件，然后按照目标尺寸进行等比例缩放，
最后覆盖原来的文件。注意，该脚本不会保留原图像的比例，因此可能会略微拉伸或压缩图像。如果需
要保留比例，请修改代码中的`Image.ANTIALIAS`参数。'''

from PIL import Image
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python resize_images.py <folder-path>")
    sys.exit()

SOURCE_FOLDER = sys.argv[1]  # 源文件夹
TARGET_SIZE = (224, 224)  # 目标尺寸

for root, dirs, files in os.walk(SOURCE_FOLDER):
    for file in files:
        if file.endswith('.png') or file.endswith('.jpg') :
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                img = Image.open(f)
                img = img.resize(TARGET_SIZE, Image.ANTIALIAS)  # 等比例缩放图像
            with open(file_path, 'wb') as f:
                img.save(f, format='png')  # 覆盖原文件，按照PNG格式保存
