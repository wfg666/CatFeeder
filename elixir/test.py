#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
#  Created by hwx on 2021/12/16
#

import argparse
import os
import time
import datetime
import cv2
import numpy as np

import logger
from predict import Predicter


def get_args_parser():
    parser = argparse.ArgumentParser('cat classification', add_help=False)
    parser.add_argument('--class_num', default=3, type=int)
    parser.add_argument('--backbone', default='resnet18', type=str)
    parser.add_argument('--device', default='cuda', type=str, help='device to use for training / testing')
    parser.add_argument('--output_dir', default='output', type=str, help='path where to save, empty for no saving')
    parser.add_argument('--gpu_list', default='0', type=str, help='gpu list for using')
    parser.add_argument('--pretrained_model', default='output', type=str, help='model for testing')
    parser.add_argument('--path', default=os.path.join(os.path.dirname(__file__), '../data/train'), type=str)
    parser.add_argument('--input_size1', default=224, type=int, help='image width')
    parser.add_argument('--input_size2', default=224, type=int, help='image height')
    return parser

def test_one_model(model):
    predicter = Predicter(model)

    ts = time.strftime("%Y%m%d_%H%M", time.localtime())
    os.makedirs(args.output_dir, exist_ok=True)
    log = logger.get_logger(filename=args.output_dir+'/test_{}.log'.format(ts))

    log.info("******** Testing model at " + predicter.args.pretrained_model)
    
    # start testing
    start_time = time.time()

    results = {}
    np.set_printoptions(precision=3)
    for subdir in os.listdir(args.path):
        subdir_path = os.path.join(args.path, subdir)
        if os.path.isdir(subdir_path):
            results[subdir] = {'correct': 0, 'total': 0, 'accuracy': 0}

            for file in os.listdir(subdir_path):
                img_path = os.path.join(subdir_path, file)
                img = cv2.imread(img_path)
                class_id, probabilities = predicter.predict(img)
                
                log_str = f"image:{img_path}, prob:" + np.array2string(probabilities, formatter={'float_kind':lambda x: "%.3f" % x})
                if class_id == int(subdir):
                    results[subdir]['correct'] += 1
                    log.debug(log_str)
                else:
                    log.warning(log_str)
                results[subdir]['total'] += 1
            results[subdir]['accuracy'] = results[subdir]['correct'] / results[subdir]['total']
    
    log.info(results)
    total_time = time.time() - start_time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))
    log.info('Testing time {}'.format(total_time_str))
    
    for handler in list(log.handlers):
        handler.close()
        log.removeHandler(handler) 

def main(args):
     model = args.pretrained_model
     if os.path.isfile(model) and model.endswith('.pth'):
        test_one_model(model)
     elif os.path.isdir(model):
        for root, dirs, files in os.walk(model):
            files.sort()
            for file in files:
                if file.endswith('.pth'):
                    test_one_model(os.path.join(root, file))

if __name__ == '__main__':
    parser = get_args_parser()
    args, unknown = parser.parse_known_args()
    main(args)