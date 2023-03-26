#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

import os
import torch
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from model import model_build
import numpy as np
import cv2

class Predicter:
    def get_args_parser(self):
        parser = argparse.ArgumentParser('cat classification', add_help=False)
        parser.add_argument('--class_num', default=3, type=int)
        parser.add_argument('--backbone', default='resnet18', type=str)
        parser.add_argument('--device', default='cuda', type=str, help='device to use for training / testing')
        parser.add_argument('--gpu_list', default='0', type=str, help='gpu list for using')
        parser.add_argument('--pretrained_model', default='output/20230321_1755/checkpoint00599.pth', type=str,
                            help='model for testing')
        parser.add_argument('--input_size1', default=224, type=int, help='image width')
        parser.add_argument('--input_size2', default=224, type=int, help='image height')
        return parser
    
    def __init__(self, model_path=None):
        print("parsing arguments")
        parser = self.get_args_parser()
        self.args, unknown = parser.parse_known_args()
        if model_path:
            self.args.pretrained_model = model_path
            
        print("checking cuda")
        torch.cuda.is_available()
        os.environ['CUDA_VISIBLE_DEVICES'] = self.args.gpu_list
        device = torch.device(self.args.device)
        print(device)

        print("building model")
        model = model_build.build(self.args)
        if self.args.pretrained_model:
            print("load model parameters from {}".format(self.args.pretrained_model))
            pretrained_dict = torch.load(self.args.pretrained_model, map_location=lambda storage, loc: storage.cuda(device))
            model.load_state_dict(pretrained_dict['model'], strict=True)
        print("moving model to cuda eval")    
        self.model = model.cuda().eval()

    def predict(self, image):
        img = cv2.resize(image,  (int(self.args.input_size1), int(self.args.input_size2)))
        img = np.ascontiguousarray(np.float32(img)[..., ::-1])
        img = img.transpose(2, 0, 1) / 255.0
        img = np.expand_dims(img, axis=0)
        img = torch.from_numpy(img).float().cuda()
        out = self.model(img)
        probabilities = torch.nn.functional.softmax(out,dim=1)
        probabilities = probabilities.detach().cpu().numpy()
        class_id = np.argmax(probabilities)
        return class_id, probabilities
