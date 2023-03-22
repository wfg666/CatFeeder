#
#  Created by hwx on 2021/12/16
#

import argparse

import os
import os.path as osp
import time
import torch

from model import model_build
from utils import logger
import datetime
import cv2
import glob
import numpy as np

ts = time.strftime("%Y%m%d_%H%M", time.localtime())
os.makedirs('./output/log/', exist_ok=True)
logger = logger.get_logger(filename='./output/log/test_{}.log'.format(ts))

def get_args_parser():
    parser = argparse.ArgumentParser('cat classification', add_help=False)
    parser.add_argument('--class_num', default=3, type=int)
    parser.add_argument('--backbone', default='alexnet', type=str)
    parser.add_argument('--device', default='cuda', type=str, help='device to use for training / testing')
    parser.add_argument('--output_dir', default='output', type=str, help='path where to save, empty for no saving')
    parser.add_argument('--gpu_list', default='1', type=str, help='gpu list for using')
    parser.add_argument('--pretrained_model', default='output/20230321_1755/checkpoint00599.pth', type=str,
                        help='model for testing')
    parser.add_argument('--eval', default=True, type=bool)
    parser.add_argument('--path', default='/data/catFeeder/data/2', type=str)
    parser.add_argument('--input_size1', default=224, type=int, help='image width')
    parser.add_argument('--input_size2', default=224, type=int, help='image height')
    parser.add_argument('--mask_thr', default=0.5, type=float)
    return parser

def build_model(args):
    return model_build.build(args)

def main(args):
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_list

    device = torch.device(args.device)
    logger.info(device)

    model = build_model(args)

    if args.pretrained_model:
        logger.info("load pretrained model from {}".format(args.pretrained_model))
        pretrained_dict = torch.load(args.pretrained_model, map_location=lambda storage, loc: storage.cuda(device))
        model.load_state_dict(pretrained_dict['model'], strict=True)

    model = model.cuda().eval()

    imageList = glob.glob(osp.join(args.path, '*.jpg')) + glob.glob(osp.join(args.path, '*.png')) + glob.glob(osp.join(args.path, '*.bmp')) + glob.glob(osp.join(args.path, '*.jpeg'))

    # start training
    start_time = time.time()

    f = open('output/test.txt', 'w')
    with torch.no_grad():
        count = 0
        for imagename in imageList:
            img = cv2.imread(imagename)
            img_resize =  cv2.resize(img,  (int(args.input_size1), int(args.input_size2)))

            img_resize = np.float32(img_resize)
            img_resize = np.ascontiguousarray(img_resize[..., ::-1])
            img_resize = img_resize.transpose(2, 0, 1)
            img_resize /= 255.0

            img_resize = np.expand_dims(img_resize, axis=0)

            img_pad = torch.from_numpy(img_resize).float().cuda()
            # print(img_pad.shape)
            pred_ = model(img_pad)
            # pred_.requires_grad = False
            # pred = pred_.cpu().numpy()

            output = torch.nn.functional.softmax(pred_,dim=1)
            output = output.cpu().numpy()

            print("image: %s, c1: %.2f, c2: %.2f, c3: %.2f"%(imagename, output[0][0], output[0][1], output[0][2]))
            f.write("image: %s, c1: %.2f, c2: %.2f, c3: %.2f\n"%(imagename, output[0][0], output[0][1], output[0][2]))
            count += 1
    f.close()
    total_time = time.time() - start_time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))
    logger.info('Testing time {}'.format(total_time_str))


if __name__ == '__main__':
    parser = argparse.ArgumentParser('cat recognization testing script', parents=[get_args_parser()])
    args = parser.parse_args()
    # if args.output_dir:
    #     Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    main(args)