#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import sys
import os
import time
from cat import Cat

import servo_controller
from mqtt_uploader import mqtt_uploader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../elixir')))
from predict import Predicter
import logger


def main():
    predicter = Predicter(os.path.join(os.path.dirname(__file__), '../elixir/pretrain/maomaonet-359.pth'))
    mqtt = mqtt_uploader()

    cats = [
        Cat("小怪兽", "Monster", 130, 5, 66, 99),
        Cat("216", "216", 55, 3, 6, 1)]
        #Cat("216", "216", 55, 2, 2, 4)]

    output_dir = 'output/app'
    os.makedirs(output_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M", time.localtime())
    log = logger.get_logger(filename=os.path.join(output_dir, 'app_{}.log'.format(ts)))

    cam = cv2.VideoCapture(0)

    last_detected_cat = 0
    believed_cat = 0
    cat_seen_count = 0

    time_last_save_photo = 0
    save_photo_interval = 5.0

    predict_count = 0
    print_interval = 30  # 打印状态间隔（秒）
    time_last_print = time.time()  # 上一次打印状态的时间

    time.sleep(1)
    while True:
        # 读一张图片
        try:
            ret, frame = cam.read()
            if not ret:
                log.error('failed to grab frame. release camera and reopen in 5s.')
                cam.release()
                time.sleep(5)
                cam = cv2.VideoCapture(0)
                continue
        except Exception as e:
            log.error("failed to re initialize camera. " + e)
            continue

        # 检测一下猫猫
        detected_cat, prob = predicter.predict(frame)

        # 保存猫猫的帅照
        if detected_cat and time.time() - time_last_save_photo >= save_photo_interval:
            pic_dir = os.path.join(output_dir, "pics", str(detected_cat))
            os.makedirs(pic_dir, exist_ok=True)
            img = cv2.resize(frame,  (int(predicter.args.input_size1), int(predicter.args.input_size2)))
            cv2.imwrite(os.path.join(pic_dir, str(time.time()) + ".png"), img)
            time_last_save_photo = time.time()  # 记录打印时间


        # 连续10帧检测到同一只猫猫才相信
        if detected_cat == last_detected_cat:
            cat_seen_count += 1
        else:
            cat_seen_count = 1
            last_detected_cat = detected_cat

        if cat_seen_count >= 10 and detected_cat != believed_cat:
            if detected_cat > 0:
                log.info(cats[detected_cat - 1].name + "来了")
            else:
                log.info("猫猫走开了")
            believed_cat = detected_cat

        # 判断要不要喂
        if believed_cat > 0:
            if cats[believed_cat - 1].appear():
                log.info('喂一嘴' + cats[believed_cat - 1].name)
                servo_controller.feed()
                mqtt.publish(cats[believed_cat - 1].english_name, time.time())

        # 打log
        predict_count += 1  # 记录 get() 调用次数
        if time.time() - time_last_print >= print_interval:  # 检查是否到达打印间隔
            print("猫猫：%d 检测：%.1f fps." % (believed_cat, predict_count / (time.time() - time_last_print)), end = '  ')
            predict_count = 0
            for cat in cats:
                print(f"{cat.name}: {cat.feed_count_hour()}/{cat.max_feed_hour}, {cat.feed_count_8h()}/{cat.max_feed_8h}, "
                    f"{cat.feed_count_day()}/{cat.max_feed_day}", end = "  ")
            print('')
            time_last_print = time.time()  # 记录打印时间

        try:
            cv2.imshow('cam', frame)
            cv2.waitKey(1)
        except Exception as e:
            print('display fail.')

        time.sleep(0.02)


if __name__ == '__main__':
    main()
