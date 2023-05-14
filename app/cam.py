#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../elixir')))

def main():
    id=0
    cam = cv2.VideoCapture(id)

    time.sleep(1)
    while True:
        # 读一张图片
        try:
            ret, frame = cam.read()
            if not ret:
                print('failed to grab frame. release camera and reopen in 5s.')
                cam.release()
                time.sleep(5)
                cam = cv2.VideoCapture(id)
                continue
        except Exception as e:
            log.error("failed to re initialize camera. " + e)
            continue


        try:
            cv2.imshow('cam', frame)
            cv2.waitKey(1)
        except Exception as e:
            print('display fail.')

        time.sleep(0.02)


if __name__ == '__main__':
    main()
